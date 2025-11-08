from flask import Blueprint, jsonify

misc_bp = Blueprint("misc", __name__)

@misc_bp.route('/.well-known/assetlinks.json')
def assetlinks():
    return jsonify([
        {
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {
                "namespace": "android_app",
                "package_name": "com.jmvs.inspectionapp", 
                "sha256_cert_fingerprints": [
                    "YOUR_APP_SIGNING_CERT_SHA256" 
                ]
            }
        }
    ])
