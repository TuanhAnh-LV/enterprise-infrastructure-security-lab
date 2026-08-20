# Implementation Guide

This guide converts the lab design into repeatable deployment phases. It focuses on architecture, control objectives, validation, and evidence rather than vendor-image installation or production secrets.

## 1. Scope and success criteria

The target environment must provide:

1. Segmented network zones with predictable addressing and routing.
2. Redundant firewall and core functions without Layer-2 loops.
3. Windows identity, name resolution, address allocation, and file services.
4. Controlled Internet access, zone-to-zone access, remote access, and DMZ publishing.
5. Centralized endpoint, network, firewall, web, and IDS telemetry.
6. Repeatable tests that prove availability, enforcement, and visibility.

## 2. Logical components

| Layer | Components | Responsibility |
| --- | --- | --- |
| Hypervisor | Proxmox VE | Hosts Windows, Linux, Wazuh, Suricata, and EVE-NG VMs |
| Network emulation | EVE-NG | Runs FortiGate and Cisco lab nodes |
| Perimeter | FortiGate HA pair | Routing boundary, policy enforcement, inspection, VPN, NAT/VIP |
| Campus network | Edge, two core, access and server switches | VLAN transport, gateway redundancy, dynamic routing, access control |
| Windows platform | Windows Server 2019 and Windows clients | AD DS, DNS, DHCP, File Server, GPO and endpoint telemetry |
| DMZ | Ubuntu and Nginx | Isolated published web service |
| SOC | Wazuh and Suricata | Collection, detection, search, dashboarding and investigation |

## 3. Addressing and trust zones

| VLAN | Name | Subnet | Gateway owner | Trust policy |
| ---: | --- | --- | --- | --- |
| 10 | MGMT | `10.60.10.0/24` | FortiGate | Administrative sources only |
| 20 | SERVER | `10.60.20.0/24` | FortiGate | Required application and management flows |
| 30 | OFFICE | `10.60.30.0/24` | HSRP on core | User access through firewall policy |
| 40 | VOICE | `10.60.40.0/24` | HSRP on core | Voice-specific services only |
| 50 | GUEST | `10.60.50.0/24` | FortiGate | Internet only; deny internal destinations |
| 60 | IT | `10.60.60.0/24` | FortiGate | Privileged administration with logging |
| 70 | DMZ | `10.60.70.0/24` | FortiGate | Published service; tightly restricted internal access |
| 80 | SOC | `10.60.80.0/24` | FortiGate | Log collection and analyst access |
| 254 | TRANSIT | `10.60.254.0/29` | FortiGate and core | OSPF adjacency only |

Reserve and document fixed addresses for the domain controller, Wazuh, Suricata, Nginx, firewall management, core switches, and infrastructure interfaces before creating DHCP scopes.

## 4. Phase 1 — Build the virtual foundation

### 4.1 Create isolated connectivity

1. Create dedicated Proxmox Linux bridges for lab-only network segments.
2. Do not assign the host a Layer-3 address on bridges that only transport lab traffic.
3. Attach the required EVE-NG adapters to those bridges.
4. Attach Windows and Linux VM adapters to the bridge that represents their target zone.
5. Record the mapping between each Proxmox bridge, EVE-NG cloud object, interface, VLAN, and VM.

### 4.2 Size and deploy systems

Allocate resources according to the physical host and vendor minimums. A reasonable lab starting point is:

| System | vCPU | RAM | Storage | Notes |
| --- | ---: | ---: | ---: | --- |
| EVE-NG | 4–8 | 8–16 GB | 80+ GB | Depends on number of active appliances |
| Windows Server | 2–4 | 4–8 GB | 60+ GB | Static IP and consistent virtual NIC |
| Windows client | 2 | 4 GB | 50+ GB | Domain-joined test endpoint |
| Wazuh all-in-one | 4 | 8 GB | 80+ GB | Increase storage for longer retention |
| Suricata | 2–4 | 4 GB | 30+ GB | Monitoring and management interfaces |
| Nginx | 1–2 | 2 GB | 20+ GB | Minimal DMZ service |

### 4.3 Foundation acceptance checks

- Every VM has a documented network attachment.
- No lab bridge unintentionally exposes a management interface.
- Time synchronization is working across network devices, Windows, Linux, and Wazuh.
- A clean snapshot exists before major configuration phases.

## 5. Phase 2 — Deploy VLANs and the switching layer

1. Create VLANs consistently on both core switches and the required access/server switches.
2. Use a dedicated, unused native VLAN on every trunk.
3. Explicitly allow only the required VLANs on each trunk.
4. Disable Dynamic Trunking Protocol where supported.
5. Bundle parallel core links with LACP.
6. Use Rapid-PVST and intentionally place the root bridge per VLAN.
7. Enable PortFast and BPDU Guard only on confirmed endpoint-facing access ports.
8. Apply port security to endpoint ports after verifying the expected MAC-address behavior.

Example validation commands:

```text
show vlan brief
show interfaces trunk
show etherchannel summary
show spanning-tree root
show port-security interface <ACCESS_INTERFACE>
```

Use the sanitized [Cisco template](../configs/cisco/core-access-template.conf) as a reference.

## 6. Phase 3 — Configure gateway redundancy and routing

### 6.1 Core gateways

1. Enable Layer-3 routing on both core switches.
2. Configure unique SVI addresses on each core and a shared HSRP virtual address for the Office and Voice VLANs.
3. Split HSRP active roles across the two cores to use both paths.
4. Track upstream reachability and decrement priority on failure.
5. Add DHCP relay to the Windows DHCP server on client-facing SVIs.

### 6.2 OSPF transit

1. Establish OSPF area 0 over VLAN 254.
2. Assign unique router IDs from `10.255.255.0/24` loopbacks.
3. Make all interfaces passive by default and enable adjacency only on the transit VLAN.
4. Advertise internal core networks and loopbacks.
5. Originate the default route from FortiGate only when an Internet route is available.

Validate:

```text
show standby brief
show ip ospf neighbor
show ip route ospf
show ip route 0.0.0.0
ping <TRANSIT_PEER>
```

## 7. Phase 4 — Deploy FortiGate HA and zone policy

### 7.1 Form the HA pair

1. Use dedicated heartbeat interfaces.
2. Match HA group name, group ID, mode, and a strong unique HA secret on both members.
3. Set primary and secondary priorities deliberately.
4. Enable session pickup where appropriate for the lab.
5. Confirm the pair is synchronized before configuring downstream services.

Never publish the real HA secret or a full exported configuration. The repository template uses `<STRONG_HA_PASSWORD>`.

### 7.2 Build interfaces and routes

1. Configure the WAN and DMZ interfaces.
2. Create a redundant aggregate toward the core pair where supported by the virtual topology.
3. Create VLAN subinterfaces for zones whose gateway resides on FortiGate.
4. Form OSPF adjacency on the Transit VLAN.
5. Verify return routes exist for core-routed networks before testing firewall policy.

### 7.3 Define policy from a traffic matrix

Create an allow-list matrix before adding rules. Each row should identify source zone, destination zone, application/service, business reason, inspection profile, logging, and rule owner.

Recommended order:

1. IT to managed infrastructure — required administrative protocols only.
2. Office to required Server services — DNS, Kerberos, LDAP, SMB, NTP and other justified services.
3. Endpoint zones to SOC — Wazuh agent and approved log transport.
4. Internal zones to Internet — approved services with security profiles.
5. Guest to Internet — NAT and inspection; explicitly deny RFC1918/internal destinations.
6. DMZ inbound and outbound — only the published service and required update/DNS flows.
7. Explicit inter-zone deny with logging for visibility.

Enable traffic logging on all security-relevant allow and deny policies.

### 7.4 Apply security profiles

Attach inspection profiles according to direction and risk:

- **Certificate inspection or deep inspection:** use only where certificates and client trust are correctly managed.
- **Web and DNS filtering:** block malicious and prohibited categories; log overrides and failures.
- **Antivirus and application control:** inspect supported traffic and tune false positives.
- **IPS:** begin with relevant server/client filters, monitor, then move to blocking after validation.

### 7.5 Publish the DMZ service

1. Assign Nginx a static DMZ address and FortiGate as its default gateway.
2. Configure a minimal Nginx server block and log both access and errors.
3. Create a VIP for the required TCP port only.
4. Create a WAN-to-DMZ policy whose destination is that VIP.
5. Attach server-appropriate inspection and enable logging.
6. Ensure the FortiGate administrative GUI is not exposed on the same WAN port.
7. Confirm that the DMZ host cannot initiate unrestricted access to internal networks.

### 7.6 Configure remote access

Use IKEv2 with current algorithms, a dedicated VPN user group, a unique pre-shared key or certificate, a limited address pool, split-tunnel destinations, explicit firewall policy, and authentication logging. See the [sanitized VPN template](../configs/fortigate/remote-access-vpn.conf).

## 8. Phase 5 — Deploy Windows services

### 8.1 Active Directory and DNS

1. Assign the server a static address in the Server zone.
2. Install AD DS and DNS, then create the lab forest using a non-public test name such as `lvta-lab.test`.
3. Create OUs by role and administration boundary rather than copying the physical organization chart.
4. Create separate administrator and standard-user accounts.
5. Configure DNS forwarders and verify domain records.
6. Join test endpoints to the domain and move them into the intended OU.

### 8.2 DHCP

1. Authorize the DHCP server in AD.
2. Create a separate scope for every client VLAN served by Windows DHCP.
3. Set the correct default gateway and internal DNS server options.
4. Exclude infrastructure ranges and create reservations where required.
5. Configure DHCP relay on the corresponding core SVI or FortiGate VLAN interface.

### 8.3 File Server and Group Policy

1. Create security groups for access control; assign permissions to groups rather than individual users.
2. Align share permissions and NTFS permissions with least privilege.
3. Apply account, firewall, antivirus, RDP, audit, PowerShell, and endpoint-hardening settings through scoped GPOs.
4. Use a pilot OU before applying a new GPO broadly.
5. Validate effective policy with `gpresult /h <REPORT_PATH>` and Event Viewer.

## 9. Phase 6 — Build centralized monitoring

### 9.1 Wazuh platform

1. Deploy Wazuh Manager, Indexer, and Dashboard in the SOC zone.
2. Restrict administrative access to the IT and SOC zones.
3. Enroll Windows endpoints with Wazuh Agent.
4. Group agents by role, such as `WIN-SERVER` and `WIN-WORKSTATION`.
5. Apply group-based collection for Sysmon, PowerShell, FIM, Registry, SCA, and Syscollector.

### 9.2 Windows telemetry

Apply a SOC audit GPO that records:

- Successful and failed logon activity.
- Credential validation and Kerberos authentication.
- User and security-group changes.
- Process creation with command-line data.
- Audit-policy and system-integrity changes.
- PowerShell Script Block Logging.

Install Sysmon with the [lab policy](../configs/sysmon/sysmon-lab.xml), then verify the `Microsoft-Windows-Sysmon/Operational` channel before restarting the Wazuh agent.

### 9.3 Network and firewall Syslog

1. Configure Wazuh to listen only on the SOC address and allow listed network-device sources.
2. Configure consistent timestamps, severity, source interface, and facility on network devices.
3. Enable FortiGate forward-traffic, local-traffic, anomaly, security, and administrative audit logs as appropriate.
4. Validate packet arrival before troubleshooting parsing or dashboard searches.

### 9.4 Suricata

1. Attach the monitoring interface to a mirrored or visibility path appropriate for the lab.
2. Keep management and monitoring interfaces logically distinct.
3. Enable EVE JSON output.
4. Use the local Wazuh agent to read `eve.json` and send events to the manager.
5. Confirm timestamps and interface names before tuning detections.

See [Security monitoring design](security-monitoring.md) for the data-source and triage model.

## 10. Phase 7 — Validate and document

Test one control at a time and record:

- Test ID and objective.
- Preconditions and source/destination.
- Exact action performed.
- Expected and observed result.
- Device, endpoint, and SIEM evidence.
- Timestamp and responsible tester.
- Remediation and retest result when a check fails.

Start with availability and routing, continue with policy enforcement, then verify telemetry and alert handling. The complete matrix is in [Validation and evidence](validation-and-evidence.md).

## 11. Deployment completion checklist

- [ ] Asset list, addressing, interfaces, and topology are current.
- [ ] Configuration backups are stored privately and are not committed to GitHub.
- [ ] FortiGate HA and core redundancy have passed controlled failover tests.
- [ ] Every zone-to-zone flow is represented in the traffic matrix.
- [ ] Guest and DMZ isolation tests pass.
- [ ] Domain join, DNS, DHCP, and Group Policy tests pass.
- [ ] Wazuh agents are active and grouped correctly.
- [ ] Network Syslog and Suricata telemetry are searchable.
- [ ] FIM, Registry, authentication, process, and PowerShell test events are visible.
- [ ] Evidence is sanitized before publication.
- [ ] `python3 scripts/pre_publish_check.py` passes.

