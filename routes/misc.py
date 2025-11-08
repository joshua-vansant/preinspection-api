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
                    "SHA256: B6:A5:B7:17:38:87:BB:8A:3C:72:B5:52:3C:58:09:60:10:E9:33:56:7C:DA:40:4E:85:5B:67:2B:77:43:11:0D" 
                ]
            }
        }
    ])
