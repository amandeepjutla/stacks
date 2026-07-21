import requests
from urllib.parse import urlparse

def solve_with_solver(d, url):
    """Use the configured solver to bypass DDoS-Guard/Cloudflare protection."""
    if not d.solver_url:
        return False, {}, None
    
    d.logger.info("Using the solver to bypass protection challenge...")
    
    try:
        payload = {
            "cmd": "request.get",
            "url": url,
            "maxTimeout": d.solver_timeout
        }
        
        response = requests.post(
            f"{d.solver_url}/v1",
            json=payload,
            timeout=d.solver_timeout / 1000 + 10
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 'ok':
            solution = data.get('solution', {})
            cookies_list = solution.get('cookies', [])
            cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies_list}
            html_content = solution.get('response')
            
            d.logger.info(f"Solver: Success - got {len(cookies_dict)} cookies")

            # Extract domain from URL
            actual_domain = urlparse(url).netloc.split(':')[0]

            # Apply cookies to session with proper domain
            for name, value in cookies_dict.items():
                d.session.cookies.set(name, value, domain=actual_domain)

            # Cache cookies for this domain (for reuse on retry/future downloads)
            d.save_cookies_to_cache(cookies_dict, domain=url)

            return True, cookies_dict, html_content
        else:
            error_msg = data.get('message', 'Unknown error')
            d.logger.error(f"Solver failed: {error_msg}")
            return False, {}, None
            
    except requests.Timeout:
        d.logger.error("Solver timeout")
        return False, {}, None
    except Exception as e:
        d.logger.error(f"Solver error: {e}")
        return False, {}, None