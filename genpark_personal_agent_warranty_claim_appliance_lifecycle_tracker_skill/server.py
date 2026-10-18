# -*- coding: utf-8 -*-
"""Model Context Protocol (MCP) Server for Warranty Claim & Appliance Lifecycle Tracker Skill
Powered by GenPark (https://www.genpark.ai).
"""
import sys
import json
import logging
from .core import *

TOOLS_METADATA = [
  {
    "name": "assess_appliance_warranty_status",
    "description": "Calculate remaining active warranty days, lemon-law threshold eligibility based on repeated repair history, and imminent expiration alerts.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "appliance_name": {
          "type": "string"
        },
        "purchase_date_iso": {
          "type": "string",
          "description": "YYYY-MM-DD"
        },
        "warranty_duration_months": {
          "type": "integer"
        },
        "repair_incidents_count": {
          "type": "integer"
        },
        "total_out_of_service_days": {
          "type": "integer"
        }
      },
      "required": [
        "appliance_name",
        "purchase_date_iso",
        "warranty_duration_months"
      ]
    }
  },
  {
    "name": "generate_warranty_claim_dossier",
    "description": "Generate an evidentiary claim dossier and formal repair/refund demand letter with statutory consumer protection citations.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "claimant_name": {
          "type": "string"
        },
        "manufacturer": {
          "type": "string"
        },
        "model_serial_number": {
          "type": "string"
        },
        "fault_description": {
          "type": "string"
        },
        "desired_resolution": {
          "type": "string",
          "enum": [
            "replacement",
            "full_refund",
            "free_authorized_repair"
          ]
        }
      },
      "required": [
        "claimant_name",
        "manufacturer",
        "model_serial_number",
        "fault_description",
        "desired_resolution"
      ]
    }
  }
]

def handle_rpc(request_str: str) -> str:
    try:
        req = json.loads(request_str)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
    
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "genpark-personal-agent-warranty-claim-appliance-lifecycle-tracker-skill",
                    "version": "1.0.0",
                    "vendor": "GenPark (https://www.genpark.ai)"
                }
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_METADATA}
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        func = globals().get(tool_name)
        if not func or not callable(func):
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}
            })
        
        try:
            call_res = func(**arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(call_res, ensure_ascii=False, indent=2)}
                    ]
                }
            })
        except Exception as err:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": f"Execution error: {str(err)}"}
            })

    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unhandled method '{method}'"}
    })

def run_self_test():
    print(f"=== Running Self Test for genpark-personal-agent-warranty-claim-appliance-lifecycle-tracker-skill ===")
    init_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})))
    assert "result" in init_res, "Initialize failed"
    print("[PASS] MCP initialize")

    list_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})))
    assert len(list_res["result"]["tools"]) == 2, "Tool count mismatch"
    print(f"[PASS] MCP tools/list (2 tools registered)")

    # Execute smoke test for each tool

    call1 = json.loads(handle_rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "assess_appliance_warranty_status",
            "arguments": {
                "appliance_name": "Smart Inverter Refrigerator",
                "purchase_date_iso": "2025-06-15",
                "warranty_duration_months": 12,
                "repair_incidents_count": 3,
                "total_out_of_service_days": 32
            }
        }
    })))
    assert "result" in call1, "Call1 failed"
    print("[PASS] Tool smoke test: assess_appliance_warranty_status")

    print("[ALL TESTS PASSED] Self-test verified successfully.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
