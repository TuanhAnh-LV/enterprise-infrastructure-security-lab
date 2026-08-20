# Validation and Evidence

Validation proves three distinct properties:

- **Availability:** the intended service works.
- **Enforcement:** prohibited access is blocked.
- **Visibility:** the action produces usable telemetry.

## Test record template

Use one record per test:

```text
Test ID:
Objective:
Date/time (UTC):
Source and destination:
Preconditions:
Action:
Expected result:
Observed result:
Evidence files:
Result: PASS / FAIL / PARTIAL
Issue and remediation:
Retest result:
```

## Validation matrix

| ID | Area | Test action | Expected result | Evidence |
| --- | --- | --- | --- | --- |
| NET-01 | VLAN | Inspect VLAN database and trunk allow lists | VLANs are consistent and only required VLANs traverse each trunk | `show vlan brief`, `show interfaces trunk` |
| NET-02 | LACP | Inspect the core port channel and interrupt one member | Bundle remains up with reduced capacity | EtherChannel summary before/after |
| NET-03 | STP | Inspect root role per VLAN | Intended core is root; no unexpected blocked access link | STP root output |
| NET-04 | HSRP | Verify active/standby, then interrupt tracked path | Virtual gateway moves to the healthy core | HSRP output and timestamps |
| NET-05 | OSPF | Verify neighbors and learned routes | Full adjacency and expected routes only | Neighbor and routing table output |
| NET-06 | DHCP relay | Renew clients in Office and IT | Correct subnet, gateway, DNS and lease server | Client lease and DHCP record |
| SEC-01 | HA | Perform a controlled primary failover | Secondary becomes active and config remains synchronized | HA status before/after |
| SEC-02 | Segmentation | Test approved and prohibited inter-zone flows | Allow-listed flows pass; others are logged and denied | Connectivity result and traffic log |
| SEC-03 | Guest isolation | Access Internet and internal addresses from Guest | Internet passes; all internal zones fail | Client test and deny log |
| SEC-04 | Security profiles | Use safe vendor-provided test categories/files | Corresponding profile logs or blocks according to policy | Security event and policy ID |
| SEC-05 | VPN | Authenticate a lab user and reach split destinations | Tunnel established; only approved lab networks routed | VPN status, route, auth log |
| DMZ-01 | VIP | Request the published Nginx service | Request reaches Nginx through the intended VIP/policy | Firewall and Nginx logs |
| DMZ-02 | Isolation | Attempt unapproved DMZ-to-internal connection | Request is denied and logged | Firewall deny record |
| WIN-01 | Domain | Join a client and resolve domain records | Join succeeds and domain DNS resolves | System properties and DNS query |
| WIN-02 | GPO | Refresh policy and generate an effective-policy report | Intended policies apply to the correct OU | `gpresult` report and GPO scope |
| MON-01 | Agent | Check Wazuh agent status and last-seen time | Endpoint is active with the correct group | Agent inventory screenshot |
| MON-02 | Authentication | Perform an authorized failed and successful test logon | Corresponding Windows events are searchable | Event details with test timestamp |
| MON-03 | Process | Launch a harmless standard process | Security/Sysmon process event includes parent and command line | Event 4688 and Sysmon 1 |
| MON-04 | PowerShell | Run a harmless local command | Script-block or process telemetry appears | PowerShell and process events |
| MON-05 | FIM | Create and modify a test file in `C:\SOC-Lab` | Integrity change is detected | File metadata and Wazuh alert |
| MON-06 | Registry | Change a disposable lab-only test value | Registry telemetry appears | Before/after value and event |
| MON-07 | Syslog | Change a lab interface description and restore it | Device event reaches and is indexed by Wazuh | Device log and Wazuh record |
| MON-08 | Suricata | Generate benign DNS/HTTP lab traffic | EVE JSON event is created and searchable | EVE record and Wazuh event |

## Useful verification commands

### Cisco IOS-style lab nodes

```text
show interfaces status
show interfaces trunk
show etherchannel summary
show spanning-tree root
show standby brief
show ip ospf neighbor
show ip route
show logging
```

### FortiGate

```text
get system ha status
get router info ospf neighbor
get router info routing-table all
show firewall policy
show firewall vip
show log syslogd setting
```

### Windows

```powershell
ipconfig /all
Resolve-DnsName lvta-lab.test
gpupdate /force
gpresult /r
Get-Service WazuhSvc, Sysmon64
Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 10
```

### Wazuh and Syslog listener

```bash
sudo /var/ossec/bin/wazuh-control status
sudo /var/ossec/bin/agent_control -lc
sudo /var/ossec/bin/wazuh-remoted -t
sudo tcpdump -ni any udp port 514
```

## Evidence quality standard

Good evidence is readable, minimal, timestamped, linked to a test ID, and sufficient to prove the expected outcome. Capture both the enforcement point and the monitoring result when possible.

Before publication:

1. Crop unrelated windows and notifications.
2. Redact credentials, tokens, license IDs, personal information, and non-lab addresses.
3. Keep commands and results readable.
4. Use neutral filenames such as `NET-05-ospf-neighbors.png`.
5. Add a one-line caption explaining what the image proves.
6. Run the pre-publication checker.

