# Sanitized Configuration Templates

These files document the lab's implementation logic while keeping credentials and private material out of the public repository.

| Path | Purpose |
| --- | --- |
| `cisco/core-access-template.conf` | VLANs, trunks, LACP, STP, HSRP, OSPF, access security and Syslog |
| `fortigate/ha-routing-firewall.conf` | HA, interfaces, VLANs, routing objects and representative firewall policies |
| `fortigate/remote-access-vpn.conf` | IKEv2 split-tunnel remote-access design |
| `fortigate/syslog.conf` | Centralized FortiGate logging to Wazuh |
| `wazuh/windows-agent.conf` | Windows event channels, FIM, Registry, inventory and SCA |
| `wazuh/suricata-integration.xml` | Collection of Suricata EVE JSON |
| `sysmon/sysmon-lab.xml` | Lab telemetry for process, network, DNS, file and Registry activity |
| `nginx/lvta-lab.conf` | Minimal DMZ web virtual host with security headers and logs |

## Safe usage

1. Treat every file as a reference template.
2. Check syntax against the exact software release in the lab.
3. Replace `<PLACEHOLDER>` values only in a private working copy.
4. Keep live exports, certificates, keys, logs and packet captures outside Git.
5. Validate each change in an isolated lab and keep a rollback point.
6. Run `python3 scripts/pre_publish_check.py` before committing.

