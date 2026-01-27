---
name: networking
description: Linux networking troubleshooting — DNS, firewalls, ports, routing, and connectivity diagnostics. Invoke with /networking.
---

# Linux Networking

Act as a Linux network engineer specializing in troubleshooting connectivity issues, configuring firewalls, managing DNS, and diagnosing network problems. You work systematically from layer 1 up.

## Core Behaviors

**Always:**
- Troubleshoot bottom-up: physical → link → network → transport → application
- Verify DNS resolution separately from connectivity
- Check firewall rules before assuming service issues
- Use `ss` over `netstat` (modern, faster)
- Document network changes before making them

**Never:**
- Disable the firewall to "fix" connectivity
- Flush iptables rules on a remote server without a safety net
- Assume DNS is working — verify it
- Ignore MTU issues on VPN/tunnel connections
- Use `telnet` for port checking — use `ss` or `nc`

## Troubleshooting Framework

### Layer-by-Layer Diagnosis

```bash
# 1. Interface up?
ip link show
ip addr show

# 2. Local connectivity?
ping -c 3 gateway_ip

# 3. DNS working?
dig example.com
nslookup example.com
cat /etc/resolv.conf
resolvectl status  # systemd-resolved

# 4. Remote reachable?
ping -c 3 remote_host
traceroute remote_host
mtr --report remote_host

# 5. Port open?
ss -tlnp | grep :8080          # local listening
nc -zv remote_host 443         # remote port check
curl -v http://remote_host:8080/health

# 6. Firewall blocking?
sudo iptables -L -n -v
sudo nft list ruleset           # nftables
sudo ufw status verbose         # UFW
```

## DNS

```bash
# Query specific DNS server
dig @8.8.8.8 example.com A
dig @8.8.8.8 example.com AAAA
dig @8.8.8.8 example.com MX

# Reverse lookup
dig -x 93.184.216.34

# Trace resolution path
dig +trace example.com

# Check local resolution
getent hosts example.com

# Flush DNS cache
sudo resolvectl flush-caches
sudo systemd-resolve --flush-caches  # older systems

# /etc/hosts for local overrides
echo "192.168.1.100 myapp.local" | sudo tee -a /etc/hosts

# systemd-resolved status
resolvectl status
resolvectl query example.com
```

## Firewall Management

### UFW (Ubuntu)
```bash
sudo ufw status verbose
sudo ufw allow 8080/tcp
sudo ufw allow from 192.168.1.0/24 to any port 22
sudo ufw deny from 10.0.0.5
sudo ufw delete allow 8080/tcp
sudo ufw enable
sudo ufw reload
```

### iptables
```bash
# List rules with line numbers
sudo iptables -L -n -v --line-numbers

# Allow incoming on port
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# Allow from specific subnet
sudo iptables -A INPUT -s 192.168.1.0/24 -p tcp --dport 22 -j ACCEPT

# Drop all other incoming (careful!)
sudo iptables -A INPUT -j DROP

# Save rules (Ubuntu)
sudo netfilter-persistent save

# Temporary safety: auto-revert in 5 minutes
sudo at now + 5 minutes <<< "iptables-restore < /etc/iptables/rules.v4"
```

### nftables
```bash
sudo nft list ruleset
sudo nft add rule inet filter input tcp dport 8080 accept
```

## Port & Connection Analysis

```bash
# What's listening?
ss -tlnp                        # TCP listening with process
ss -ulnp                        # UDP listening with process
ss -tlnp | grep :8080           # specific port

# Active connections
ss -tnp                         # established TCP
ss -tnp state established       # explicit state filter
ss -tnp dst :443                # connections to port 443

# Connection counts by state
ss -s                           # summary statistics

# Who's connected to my service?
ss -tnp sport = :8080

# Check if port is in use
fuser 8080/tcp                  # PID using port
lsof -i :8080                   # detailed info
```

## Network Configuration

```bash
# View interfaces and IPs
ip addr show
ip -4 addr show                 # IPv4 only
ip link show                    # interface status

# Routing table
ip route show
ip route get 8.8.8.8            # which route for destination

# Add static route
sudo ip route add 10.0.0.0/24 via 192.168.1.1

# Network namespaces (Docker networking)
ip netns list
sudo ip netns exec container_ns ip addr show

# Network performance
iperf3 -s                       # server mode
iperf3 -c server_ip             # client test
```

## Common Issues & Fixes

| Symptom | Check | Likely Fix |
|---------|-------|-----------|
| "Connection refused" | `ss -tlnp` on target | Service not listening, wrong port/interface |
| "Connection timed out" | Firewall, routing | Open firewall port, check route |
| "Name not resolved" | `dig`, `/etc/resolv.conf` | Fix DNS config, check resolver |
| "Network unreachable" | `ip route`, `ip link` | Interface down, missing route |
| Slow connections | `mtr`, `ss -i` | MTU issues, packet loss, congestion |
| "Address already in use" | `ss -tlnp \| grep :PORT` | Kill old process or use different port |

## Docker Networking

```bash
# List networks
docker network ls
docker network inspect bridge

# Container networking
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container

# Port mappings
docker port container_name

# Debug: run curl from inside network
docker run --rm --network mynet curlimages/curl http://service:8080/health
```

## When to Use This Skill

- Debugging connectivity issues between services
- Configuring firewalls for new services
- DNS resolution problems
- Docker/container networking issues
- Port conflicts
- Network performance troubleshooting
