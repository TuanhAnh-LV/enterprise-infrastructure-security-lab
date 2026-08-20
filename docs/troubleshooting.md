# Troubleshooting Notes

Troubleshoot from the lowest relevant layer upward and change one variable at a time. Record the original state before modifying configuration.

## Endpoint has no connectivity

1. Confirm virtual NIC attachment and Proxmox/EVE-NG bridge mapping.
2. Check link state, access VLAN, trunk allow list, native VLAN, and spanning tree.
3. Verify address, mask, gateway, DHCP lease, and DNS server.
4. Confirm HSRP state and the endpoint ARP entry.
5. Check the routing table and FortiGate return path.
6. Review firewall policy order, source/destination objects, service, NAT, and traffic logs.

## OSPF adjacency does not form

- Confirm both peers share the same subnet, area, timers, network type, and authentication settings.
- Check that VLAN 254 is present and permitted end to end.
- Ensure the transit interface is not passive.
- Verify unique router IDs and that no access policy blocks the protocol.
- Inspect logs and neighbor state before restarting a routing process.

## HSRP gateway is unstable

- Check duplicate addresses, priority, preemption delay, and tracked-route behavior.
- Verify the intended STP root aligns with the preferred gateway path.
- Confirm inter-core LACP and trunk consistency.
- Look for link flaps and CPU/resource pressure in the emulator.

## DHCP relay fails

- Confirm the scope is active and has free leases.
- Verify gateway and DNS options match the target subnet.
- Confirm the relay/helper address points to the correct server.
- Check UDP 67/68 policy and routing in both directions.
- Verify the DHCP server is authorized in AD and bound to the correct interface.

## Domain join or DNS fails

- Make the client use the domain DNS server, not a public resolver.
- Verify forward and reverse resolution and system time.
- Confirm required AD traffic is allowed between the client and Server zone.
- Check that the client and DC are not using overlapping hostnames or stale records.
- Review Windows DNS, Netlogon, and System events.

## FortiGate HA is not synchronized

- Confirm group settings and heartbeat-interface order match.
- Verify heartbeat links are isolated and operational.
- Check model/version compatibility and interface mapping in EVE-NG.
- Inspect HA checksums and synchronization status before forcing failover.
- Do not repeatedly reboot both members; preserve one known-good control plane.

## Firewall policy appears correct but traffic fails

- Verify the session matches the expected ingress interface, source, destination, service, schedule, and policy order.
- Confirm a return route exists.
- Check VIP destination mapping and port translation.
- Review SSL/security-profile blocks separately from base policy denies.
- Use packet capture and flow debugging only in the isolated lab, with narrow filters and a short collection window.

## Wazuh agent is disconnected

- Confirm endpoint time, DNS/address, routes, and firewall policy to the manager.
- Check the local `WazuhSvc` service and agent log.
- Verify enrollment and agent identity; remove stale duplicate registrations carefully.
- Confirm the manager services and listener ports are available.
- Reconnect first, then investigate missing individual event channels.

## Windows events are missing

- Verify the GPO is linked to the correct OU and appears in `gpresult`.
- Confirm the Windows event channel contains recent events locally.
- Check Wazuh group assignment and merged agent configuration.
- Avoid declaring the same channel in multiple places.
- Confirm the Wazuh agent restarted after policy changes.

## Sysmon events are missing

- Confirm `Sysmon64` is running.
- Validate the XML syntax and installed configuration.
- Check `Microsoft-Windows-Sysmon/Operational` locally.
- Generate a harmless event that matches the include rules.
- Verify the Wazuh agent collects that exact channel.

## Network Syslog does not appear in Wazuh

1. Use a packet capture on the manager to prove whether UDP 514 arrives.
2. Confirm source interface/address and allowed-source list.
3. Check local firewall and Wazuh remote-listener syntax.
4. Validate Wazuh configuration before restarting the manager.
5. If raw packets arrive but no searchable event exists, investigate decoder/index/query behavior.

## Suricata events are missing

- Confirm the monitored interface receives the intended traffic.
- Verify Suricata service health and EVE JSON output path.
- Check that the EVE file is current and valid JSON.
- Confirm file permissions allow the local Wazuh agent to read it.
- Check the Wazuh `localfile` path and JSON log format.

