# swapfile-config

Creates a swapfile of specified size and mounts.

## Requirements

*None*

## Role Variables

Define the following variables in your inventory or playbook to create, update
and remove admin users:

These values are set as defaults.

```
# Use any of the following suffixes
# c=1
# w=2
# b=512
# kB=1000
# K=1024
# MB=1000*1000
# M=1024*1024
# xM=M
# GB=1000*1000*1000
# G=1024*1024*1024
swap_file_size: 1G
swap_file_path: /swapfile
```

## Dependencies
*None*

## Example Playbook

The following playbook updates admin users on dev and prod servers with
different options:

    - hosts: dev-servers
      roles:
        - role: swapfile-config
          swap_file_path: /swapfile
          swap_file_size: 1G
     - hosts: prod-servers
       roles:
         - role: swapfile-config
           swap_file_path: /swapfile
           swap_file_size: 2G
