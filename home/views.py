import requests
from django.conf import settings
from django.http import HttpResponse


def index(request):
    query = request.GET.get("query", "").strip()

    patent_data = None
    error_message = None
    searched = False

    if query:
        searched = True
        try:
            resp = requests.post(
                f"{settings.TIP_API_URL}/v1/patent-lookup/search",
                headers={
                    "x-api-key": settings.TIP_API_TOKEN,
                    "Content-Type": "application/json",
                },
                json={"query": query},
                timeout=15,
            )
            if resp.status_code == 200:
                payload = resp.json()
                if payload.get("status"):
                    patent_data = payload.get("data", {})
                else:
                    error_message = payload.get("message", "No patent found for the given identifier.")
            elif resp.status_code == 401:
                error_message = "API authentication failed (401). Please check your API key."
            elif resp.status_code == 403:
                error_message = "Access forbidden (403). This endpoint is not enabled for your API key."
            elif resp.status_code == 429:
                error_message = "Daily quota exceeded (429). Please try again tomorrow."
            else:
                error_message = f"API returned an unexpected status code: {resp.status_code}."
        except requests.exceptions.ConnectionError:
            error_message = "Could not connect to the TIP API. Please verify the API URL is reachable."
        except requests.exceptions.Timeout:
            error_message = "The request to the TIP API timed out. Please try again."
        except Exception as exc:
            error_message = f"An unexpected error occurred: {exc}"

    # ── Extract fields from the API response ──────────────────────────────────
    def safe(obj, *keys, default="—"):
        """Safely traverse nested dicts."""
        for k in keys:
            if not isinstance(obj, dict):
                return default
            obj = obj.get(k)
        return obj if obj not in (None, "", []) else default

    details_html = ""
    quota_html = ""

    if patent_data:
        app = patent_data.get("application", {})
        jurisdiction = patent_data.get("jurisdiction", "—").upper()

        # ── Fields mapping ────────────────────────────────────────────────────
        # Attorney name
        attorney_name = safe(app, "attorney_name")
        if attorney_name == "—":
            attorney_name = safe(app, "attorney", "name")
        if attorney_name == "—":
            attorney_name = safe(app, "prosecuting_attorney")

        # Law firm name
        law_firm = safe(app, "law_firm_name")
        if law_firm == "—":
            law_firm = safe(app, "law_firm")
        if law_firm == "—":
            law_firm = safe(app, "firm_name")

        # Assignee
        assignee = safe(app, "assigneeName")
        if assignee == "—":
            assignee = safe(app, "assignee_name")
        if assignee == "—":
            assignee = safe(app, "assignee")

        # Examiner
        examiner = safe(app, "examiner_name")
        if examiner == "—":
            examiner = safe(app, "examiner", "name")
        if examiner == "—":
            examiner = safe(app, "primary_examiner")

        # Filing date
        filing_date = safe(app, "filing_date")
        if filing_date == "—":
            filing_date = safe(app, "filingDate")

        # Disposal / application status
        disposal_status = safe(app, "app_status")
        if disposal_status == "—":
            disposal_status = safe(app, "status")
        if disposal_status == "—":
            disposal_status = safe(app, "disposal_status")

        # Extra useful identifiers
        title = safe(app, "title", default="N/A")
        app_number = patent_data.get("application_number") or safe(app, "application_number")
        patent_num = safe(app, "patent_num")
        pub_number = safe(app, "publication_number")
        entity_size = safe(app, "entity_size")
        inventors = safe(app, "inventors")

        # Quota info
        quota = patent_data.get("quota", {})
        if quota:
            quota_html = f"""
            <div class="tip-card" style="margin-top:16px;padding:14px 20px;
                         display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
                <span style="font-size:13px;color:var(--tip-text-secondary);">
                    &#128202;&nbsp;API Quota &mdash;
                    <strong>{quota.get('used', '?')}</strong> used &nbsp;/&nbsp;
                    <strong>{quota.get('remaining', '?')}</strong> remaining
                    (limit: {quota.get('limit', '?')})
                </span>
            </div>"""

        def status_tag(val):
            """Pick a semantic TIP tag class based on disposal status text."""
            if val == "—":
                return "tip-tag tip-tag-default"
            lower = val.lower()
            if any(x in lower for x in ("patent", "grant", "issue", "allow")):
                return "tip-tag tip-tag-success"
            if any(x in lower for x in ("pending", "process")):
                return "tip-tag tip-tag-warning"
            if any(x in lower for x in ("abandon", "expire", "reject")):
                return "tip-tag tip-tag-error"
            return "tip-tag tip-tag-default"

        details_html = f"""
        <!-- ── Patent Header Card ─────────────────────────────────── -->
        <div class="tip-card" style="margin-top:32px;">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;
                        flex-wrap:wrap;gap:12px;margin-bottom:20px;">
                <div>
                    <h2 style="margin:0 0 6px;font-size:20px;font-weight:700;
                               color:var(--tip-primary);">{title}</h2>
                    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
                        <span class="tip-tag tip-tag-primary">Jurisdiction: {jurisdiction}</span>
                        {f'<span class="tip-tag tip-tag-default">App&nbsp;#&nbsp;{app_number}</span>' if app_number and app_number != "—" else ""}
                        {f'<span class="tip-tag tip-tag-default">Patent&nbsp;#&nbsp;{patent_num}</span>' if patent_num and patent_num != "—" else ""}
                        {f'<span class="tip-tag tip-tag-default">Pub&nbsp;#&nbsp;{pub_number}</span>' if pub_number and pub_number != "—" else ""}
                    </div>
                </div>
                <span class="{status_tag(disposal_status)}"
                      style="font-size:14px;padding:6px 14px;">
                    {disposal_status}
                </span>
            </div>

            <!-- ── Key Details Grid ──────────────────────────────── -->
            <div class="tip-stats-row" style="gap:16px;flex-wrap:wrap;">

                <div class="tip-card" style="flex:1;min-width:200px;background:var(--tip-bg-alt,#f9fafb);">
                    <div style="font-size:12px;text-transform:uppercase;letter-spacing:.05em;
                                color:var(--tip-text-secondary);margin-bottom:6px;">
                        &#9878;&nbsp; Attorney Name
                    </div>
                    <div style="font-size:16px;font-weight:600;">{attorney_name}</div>
                </div>

                <div class="tip-card" style="flex:1;min-width:200px;background:var(--tip-bg-alt,#f9fafb);">
                    <div style="font-size:12px;text-transform:uppercase;letter-spacing:.05em;
                                color:var(--tip-text-secondary);margin-bottom:6px;">
                        &#127970;&nbsp; Law Firm
                    </div>
                    <div style="font-size:16px;font-weight:600;">{law_firm}</div>
                </div>

                <div class="tip-card" style="flex:1;min-width:200px;background:var(--tip-bg-alt,#f9fafb);">
                    <div style="font-size:12px;text-transform:uppercase;letter-spacing:.05em;
                                color:var(--tip-text-secondary);margin-bottom:6px;">
                        &#127970;&nbsp; Assignee
                    </div>
                    <div style="font-size:16px;font-weight:600;">{assignee}</div>
                </div>

            </div>

            <div class="tip-stats-row" style="gap:16px;flex-wrap:wrap;margin-top:16px;">

                <div class="tip-card" style="flex:1;min-width:200px;background:var(--tip-bg-alt,#f9fafb);">
                    <div style="font-size:12px;text-transform:uppercase;letter-spacing:.05em;
                                color:var(--tip-text-secondary);margin-bottom:6px;">
                        &#128100;&nbsp; Examiner Name
                    </div>
                    <div style="font-size:16px;font-weight:600;">{examiner}</div>
                </div>

                <div class="tip-card" style="flex:1;min-width:200px;background:var(--tip-bg-alt,#f9fafb);">
                    <div style="font-size:12px;text-transform:uppercase;letter-spacing:.05em;
                                color:var(--tip-text-secondary);margin-bottom:6px;">
                        &#128197;&nbsp; Filing Date
                    </div>
                    <div style="font-size:16px;font-weight:600;">{filing_date}</div>
                </div>

                <div class="tip-card" style="flex:1;min-width:200px;background:var(--tip-bg-alt,#f9fafb);">
                    <div style="font-size:12px;text-transform:uppercase;letter-spacing:.05em;
                                color:var(--tip-text-secondary);margin-bottom:6px;">
                        &#128204;&nbsp; Disposal Status
                    </div>
                    <div style="font-size:16px;font-weight:600;">
                        <span class="{status_tag(disposal_status)}">{disposal_status}</span>
                    </div>
                </div>

            </div>
        </div>

        <!-- ── Additional Details Table ───────────────────────────── -->
        <div class="tip-card" style="margin-top:24px;padding:0;">
            <div style="padding:20px 24px 12px;">
                <h3 style="margin:0;font-size:16px;font-weight:600;">Additional Details</h3>
                <p style="margin:4px 0 0;font-size:13px;color:var(--tip-text-secondary);">
                    Full application record returned by the TIP API
                </p>
            </div>
            <div class="tip-table-wrap">
                <table class="tip-table">
                    <thead>
                        <tr>
                            <th style="width:220px;">Field</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="color:var(--tip-text-secondary);font-weight:500;">Attorney Name</td>
                            <td>{attorney_name}</td>
                        </tr>
                        <tr>
                            <td style="color:var(--tip-text-secondary);font-weight:500;">Law Firm Name</td>
                            <td>{law_firm}</td>
                        </tr>
                        <tr>
                            <td style="color:var(--tip-text-secondary);font-weight:500;">Assignee Name</td>
                            <td>{assignee}</td>
                        </tr>
                        <tr>
                            <td style="color:var(--tip-text-secondary);font-weight:500;">Examiner Name</td>
                            <td>{examiner}</td>
                        </tr>
                        <tr>
                            <td style="color:var(--tip-text-secondary);font-weight:500;">Filing Date</td>
                            <td>{filing_date}</td>
                        </tr>
                        <tr>
                            <td style="color:var(--tip-text-secondary);font-weight:500;">Disposal Status</td>
                            <td>
                                <span class="{status_tag(disposal_status)}">{disposal_status}</span>
                            </td>
                        </tr>
                        <tr>
                            <td style="color:var(--tip-text-secondary);font-weight:500;">Inventors</td>
                            <td>{inventors}</td>
                        </tr>
                        <tr>
                            <td style="color:var(--tip-text-secondary);font-weight:500;">Entity Size</td>
                            <td>{entity_size}</td>
                        </tr>
                        <tr>
                            <td style="color:var(--tip-text-secondary);font-weight:500;">Jurisdiction</td>
                            <td>{jurisdiction}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        {quota_html}
        """

    # ── Error block ───────────────────────────────────────────────────────────
    error_html = ""
    if error_message:
        error_html = f"""
        <div class="tip-card" style="margin-top:32px;border-left:4px solid var(--tip-error,#e53e3e);
                                      padding:20px 24px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <span class="tip-tag tip-tag-error">Error</span>
                <strong style="font-size:15px;">Could not retrieve patent data</strong>
            </div>
            <p style="margin:0;color:var(--tip-text-secondary);font-size:14px;">{error_message}</p>
        </div>"""

    # ── Empty state (searched but no result, no explicit error) ──────────────
    empty_html = ""
    if searched and not patent_data and not error_message:
        empty_html = """
        <div class="tip-card" style="margin-top:32px;text-align:center;padding:48px 24px;">
            <div style="font-size:40px;margin-bottom:12px;">&#128269;</div>
            <h3 style="margin:0 0 8px;font-size:18px;">No results found</h3>
            <p style="margin:0;color:var(--tip-text-secondary);">
                No patent matched your query. Try a different application number,
                publication number, or patent number.
            </p>
        </div>"""

    # ── Hint text shown before any search ────────────────────────────────────
    hint_html = ""
    if not searched:
        hint_html = """
        <div class="tip-card" style="margin-top:32px;padding:32px 28px;">
            <h3 style="margin:0 0 12px;font-size:16px;font-weight:600;">
                &#128161;&nbsp; How to search
            </h3>
            <p style="margin:0 0 10px;color:var(--tip-text-secondary);font-size:14px;">
                Enter any of the following identifiers in the search box above and press
                <strong>Search Patent</strong>:
            </p>
            <div class="tip-table-wrap">
                <table class="tip-table">
                    <thead>
                        <tr><th>Type</th><th>Example</th></tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>US Application Number</td>
                            <td><code>16/687,273</code>&nbsp;or&nbsp;<code>16687273</code></td>
                        </tr>
                        <tr>
                            <td>US Publication Number</td>
                            <td><code>US20200123456A1</code></td>
                        </tr>
                        <tr>
                            <td>US Patent Number</td>
                            <td><code>US8623891</code>&nbsp;or&nbsp;<code>8623891</code></td>
                        </tr>
                        <tr>
                            <td>EP / Foreign Number</td>
                            <td><code>EP1514569A1</code></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>"""

    # ── Assemble the full page ────────────────────────────────────────────────
    current_query_escaped = query.replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patent Lookup &mdash; TriangleIP</title>
    <link rel='stylesheet' href='/static/tip_design.css'>
    <style>
        .search-bar {{
            display: flex;
            gap: 12px;
            align-items: stretch;
            flex-wrap: wrap;
        }}
        .search-bar input {{
            flex: 1;
            min-width: 260px;
            padding: 10px 16px;
            border: 1.5px solid var(--tip-border, #d1d5db);
            border-radius: 8px;
            font-size: 15px;
            font-family: inherit;
            color: var(--tip-text, #111827);
            background: var(--tip-bg, #ffffff);
            outline: none;
            transition: border-color .15s;
        }}
        .search-bar input:focus {{
            border-color: var(--tip-primary);
        }}
        .search-bar button {{
            white-space: nowrap;
        }}
        code {{
            background: var(--tip-bg-alt, #f3f4f6);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 13px;
        }}
    </style>
</head>
<body>

<!-- ── Navbar ─────────────────────────────────────────────────────────── -->
<nav class="tip-navbar">
    <a class="tip-navbar-brand" href="/">
        &#9651;&nbsp; TriangleIP
    </a>
    <div style="display:flex;gap:8px;">
        <a href="/" class="tip-btn tip-btn-ghost">Patent Lookup</a>
    </div>
</nav>

<!-- ── Main content ───────────────────────────────────────────────────── -->
<div class="tip-page">

    <!-- Page title + subtitle -->
    <h1 class="tip-page-title">Patent Lookup</h1>
    <p style="margin:-12px 0 28px;color:var(--tip-text-secondary);font-size:15px;">
        Search any US or foreign patent by application number, publication number,
        or patent number to view its key details.
    </p>

    <!-- ── Search Card ──────────────────────────────────────────────────── -->
    <div class="tip-card">
        <h2 style="margin:0 0 16px;font-size:17px;font-weight:600;">
            &#128269;&nbsp; Search Patent
        </h2>
        <form method="GET" action="/">
            <div class="search-bar">
                <input
                    type="text"
                    name="query"
                    value="{current_query_escaped}"
                    placeholder="e.g. 16/687,273 &nbsp;|&nbsp; US8623891 &nbsp;|&nbsp; EP1514569A1"
                    autocomplete="off"
                    spellcheck="false"
                />
                <button type="submit" class="tip-btn tip-btn-primary" style="padding:10px 24px;">
                    Search Patent
                </button>
                {f'<a href="/" class="tip-btn tip-btn-ghost" style="padding:10px 18px;">Clear</a>' if query else ''}
            </div>
        </form>
    </div>

    <!-- ── Results / hints / errors ─────────────────────────────────────── -->
    {details_html}
    {error_html}
    {empty_html}
    {hint_html}

</div><!-- /tip-page -->

</body>
</html>"""

    return HttpResponse(html, content_type="text/html")
