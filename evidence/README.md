# Evidence Checklist

Evidence makes the project credible, but only publish material that has been reviewed and sanitized. Do not invent results or upload screenshots that expose passwords, keys, license information, personal data, or unrelated systems.

## Recommended evidence set

Keep the final public set small: approximately 8–12 clear images are stronger than dozens of repetitive screenshots.

| Folder | Suggested file | What it should prove |
| --- | --- | --- |
| `network/` | `NET-00-logical-topology.png` | Complete topology and zone boundaries |
| `network/` | `NET-04-hsrp-status.png` | Active/standby gateway state |
| `network/` | `NET-05-ospf-neighbors.png` | Full OSPF adjacency |
| `network/` | `NET-02-lacp-bundle.png` | Operational port channel |
| `fortigate/` | `SEC-01-ha-status.png` | Healthy Active-Passive cluster |
| `fortigate/` | `SEC-02-policy-log.png` | Expected allow/deny decision and policy ID |
| `fortigate/` | `DMZ-01-vip-and-nginx.png` | Published service and matching log |
| `windows/` | `WIN-01-domain-and-dns.png` | Domain membership and DNS resolution |
| `windows/` | `WIN-02-effective-gpo.png` | Applied audit/hardening policy |
| `wazuh/` | `MON-01-active-agents.png` | Connected endpoints and correct grouping |
| `wazuh/` | `MON-03-process-event.png` | Process, parent, command line and host context |
| `wazuh/` | `MON-05-fim-alert.png` | Authorized lab-file change detected by FIM |
| `testing/` | `validation-summary.png` | Test IDs, results and retest status |

## Screenshot standard

1. Use a resolution that keeps commands and results readable.
2. Crop browser tabs, bookmarks, desktop notifications, and unrelated windows.
3. Redact credentials, tokens, serial/license identifiers, public addresses, and personal data.
4. Preserve the device/host label, timestamp, command/query, and relevant output.
5. Add a concise caption in the pull request or in a nearby Markdown section.
6. Do not stage a screenshot until a second visual review confirms it is safe.

## Suggested Markdown pattern

After adding an approved image, reference it from the relevant document:

```markdown
![OSPF neighbors in Full state](../evidence/network/NET-05-ospf-neighbors.png)

*NET-05 — Both core switches formed the expected OSPF adjacency over the transit VLAN.*
```

The folders contain `.gitkeep` files so their intended structure appears before screenshots are added.

