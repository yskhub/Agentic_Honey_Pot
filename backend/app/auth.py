from fastapi import Header, HTTPException, Depends, Request
import os
from jose import jwt, JWTError
import requests
import time
import json
from jwcrypto import jwk as jwcrypto_jwk

# JWKS caching
_JWKS_CACHE = None
_JWKS_CACHE_TS = 0
_JWKS_CACHE_TTL = int(os.getenv('ADMIN_JWKS_CACHE_TTL', '300'))

# Optional JWKS / OIDC settings
_ADMIN_JWKS_URL = os.getenv('ADMIN_JWKS_URL')
_ADMIN_JWT_AUDIENCE = os.getenv('ADMIN_JWT_AUDIENCE')
_ADMIN_JWT_ISSUER = os.getenv('ADMIN_JWT_ISSUER')
_ADMIN_OIDC_ISSUER = os.getenv('ADMIN_OIDC_ISSUER')


# Optional JWT-based admin verification using ADMIN_AUTH_PUBLIC_KEY (PEM)
_ADMIN_PUBKEY = os.getenv('ADMIN_AUTH_PUBLIC_KEY')
_ADMIN_JWT_ALGS = os.getenv('ADMIN_AUTH_JWT_ALGS', 'RS256').split(',')

def require_api_key(x_api_key: str = Header(...)):
    expected = os.getenv("API_KEY")
    if not expected:
        raise HTTPException(status_code=500, detail="Server API key not configured")
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key


def _extract_bearer(request: Request):
    auth = request.headers.get('authorization')
    if not auth:
        return None
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return parts[1]
    return None


def _fetch_jwks():
    global _JWKS_CACHE, _JWKS_CACHE_TS
    now = int(time.time())
    if _JWKS_CACHE and (now - _JWKS_CACHE_TS) < _JWKS_CACHE_TTL:
        return _JWKS_CACHE
    # if JWKS URL not configured, attempt OIDC discovery from issuer
    jwks_url = _ADMIN_JWKS_URL
    if not jwks_url and _ADMIN_OIDC_ISSUER:
        # discover OIDC configuration
        try:
            disco_url = _ADMIN_OIDC_ISSUER.rstrip('/') + '/.well-known/openid-configuration'
            r = requests.get(disco_url, timeout=5)
            r.raise_for_status()
            conf = r.json()
            jwks_url = conf.get('jwks_uri')
        except Exception:
            jwks_url = None
    if not jwks_url:
        return None
    try:
        resp = requests.get(jwks_url, timeout=5)
        resp.raise_for_status()
        jwks = resp.json()
        _JWKS_CACHE = jwks
        _JWKS_CACHE_TS = now
        return jwks
    except Exception:
        return None


def _get_public_pem_for_kid(kid: str):
    jwks = _fetch_jwks()
    if not jwks or 'keys' not in jwks:
        return None
    for key in jwks['keys']:
        if key.get('kid') == kid:
            # convert jwk to PEM using jwcrypto
            jwk_obj = jwcrypto_jwk.JWK.from_json(json.dumps(key))
            try:
                pem = jwk_obj.export_to_pem(public_key=True, private_key=False)
            except TypeError:
                # older jwcrypto signature
                pem = jwk_obj.export_to_pem()
            return pem
    return None


def require_admin_key(request: Request, x_api_key: str = Header(None)):
    expected = os.getenv("ADMIN_API_KEY")
    if not expected:
        raise HTTPException(status_code=500, detail="Admin API key not configured")
    # Accept either x-api-key header or Authorization: Bearer <token>
    if x_api_key and x_api_key == expected:
        return x_api_key
    bearer = _extract_bearer(request)
    if bearer:
        # If ADMIN_AUTH_PUBLIC_KEY is set, validate JWT signature and optional claims
        if _ADMIN_PUBKEY:
            try:
                # Do not require audience by default; accept any valid signature
                payload = jwt.decode(bearer, _ADMIN_PUBKEY, algorithms=_ADMIN_JWT_ALGS)
                return payload
            except JWTError:
                raise HTTPException(status_code=403, detail="Invalid admin token")
        # fallback: allow bearer token equal to ADMIN_API_KEY
        # If JWKS/OIDC URL configured, attempt to validate against JWKS and claims
        if _ADMIN_JWKS_URL:
            # decode header to get kid
            try:
                header = jwt.get_unverified_header(bearer)
                kid = header.get('kid')
            except Exception:
                kid = None
            pem = None
            if kid:
                pem = _get_public_pem_for_kid(kid)
            # if no pem found, try validating with ADMIN_AUTH_PUBLIC_KEY if available
            if pem:
                try:
                    # set validation options
                    options = {}
                    # require audience/issuer if configured
                    aud = _ADMIN_JWT_AUDIENCE if _ADMIN_JWT_AUDIENCE else None
                    iss = _ADMIN_JWT_ISSUER if _ADMIN_JWT_ISSUER else None
                    payload = jwt.decode(bearer, pem, algorithms=_ADMIN_JWT_ALGS, audience=aud, issuer=iss)
                    return payload
                except JWTError:
                    raise HTTPException(status_code=403, detail="Invalid admin token")
        # fallback: allow bearer token equal to ADMIN_API_KEY
        if bearer == expected:
            return bearer
    raise HTTPException(status_code=403, detail="Admin credentials required")
