# Networking Response
## Example Output
```
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
