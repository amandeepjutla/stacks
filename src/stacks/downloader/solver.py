import requests
from urllib.parse import urlparse

def solve_with_solver(d, url):
    """Use the configured solver to bypass DDoS-Guard/Cloudflare protection.

    DDoS-Guard clearance is domain-wide via its __ddg* cookies, but Anna's Archive
    serves the slow_download endpoint's challenge on an HTTP 403 that the solver's
    browser returns *without* solving (the homepage/md5 challenges are 200-served
    and solve fine). So rather than asking the solver to clear the target URL
    directly, we clear the domain *root* — a page the solver reliably solves —
    then adopt the resulting clearance cookies and user-agent on our session and
    fetch the real target URL ourselves. DDoS-Guard binds the clearance to the
    solving browser's user-agent, so we must reuse that UA alongside the cookies.
    """
    if not d.solver_url:
        return False, {}, None

    d.logger.info("Using the solver to bypass protection challenge...")

    parsed = urlparse(url)
    actual_domain = parsed.netloc.split(':')[0]
    root_url = f"{parsed.scheme}://{parsed.netloc}/"

    try:
        payload = {
            "cmd": "request.get",
            "url": root_url,
            # Byparr expects max_timeout in seconds (FlareSolverr used maxTimeout ms);
            # send both so either solver is happy.
            "max_timeout": max(int(d.solver_timeout / 1000), 30),
            "maxTimeout": d.solver_timeout,
        }

        response = requests.post(
            f"{d.solver_url}/v1",
            json=payload,
            timeout=d.solver_timeout / 1000 + 20
        )
        response.raise_for_status()

        data = response.json()

        if data.get('status') != 'ok':
            error_msg = data.get('message', 'Unknown error')
            d.logger.error(f"Solver failed: {error_msg}")
            return False, {}, None

        solution = data.get('solution', {})
        cookies_list = solution.get('cookies', [])
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies_list}
        user_agent = solution.get('userAgent')

        d.logger.info(f"Solver: cleared {actual_domain} - got {len(cookies_dict)} cookies")

        # DDoS-Guard ties the clearance cookies to the solving browser's user-agent,
        # so match it on our session before reusing the cookies.
        if user_agent:
            d.session.headers['User-Agent'] = user_agent
        # Drop any stale cookies for this host first so leftover __ddg* values from a
        # previous (failed) solve don't shadow the fresh clearance in the jar.
        for dom in (actual_domain, '.' + actual_domain):
            try:
                d.session.cookies.clear(domain=dom)
            except KeyError:
                pass
        for name, value in cookies_dict.items():
            d.session.cookies.set(name, value, domain=actual_domain)

        # Cache clearance cookies for this domain (reused on retry/future downloads)
        d.save_cookies_to_cache(cookies_dict, domain=actual_domain)

        # Now fetch the actual target URL with the cleared session. With domain-wide
        # clearance in place, the slow_download page (or mirror page) loads normally.
        target = d.session.get(url, timeout=30)
        if target.status_code == 200:
            d.logger.info(f"Solver: fetched target after clearance ({len(target.text)} bytes)")
            return True, cookies_dict, target.text

        d.logger.warning(f"Solver: target still {target.status_code} after clearing {actual_domain}")
        return False, cookies_dict, None

    except requests.Timeout:
        d.logger.error("Solver timeout")
        return False, {}, None
    except Exception as e:
        d.logger.error(f"Solver error: {e}")
        return False, {}, None
