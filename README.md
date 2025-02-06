# Grafana Data Source Proxy Implementation Research

This repository contains the testing environment and proof-of-concept code used in my blog post about Grafana's data source proxy implementation and its security considerations: [Understanding Grafana's Data Source Proxy Implementation](https://jsnv.dev/posts/grafana_data_source_proxy_implementation/)

## Contents
- `docker-compose.yml` - Test environment with Grafana and a test server
- `grafana.ini` - Grafana configuration with data source proxy whitelist
- `server.py` - Flask server for logging incoming requests
- `poc_ssrf.py` - POC script

## Note
This code is provided for educational purposes to help understand Grafana's proxy implementation. For more details and security considerations, please refer to the blog post.

## Acknowledgments
Special thanks to the Grafana security team for their collaboration and permission to share this research.
