# SHADOWLANDS v0.16a AUDIT

## Summary

An audit of shadowlands v0.16a was performed by Christopher M. Hobbs
(cmhobbs@member.fsf.org) of Ascia Technologies, LLC on 2018-12-03.
Various methods were used to audit the code and running programs.
This report details the findings of the audit.

## General Recommendations

It is highly recommended (and hopefully painfully obvious) that
shadowlands be installed from trusted sources and run only on trusted
machines.  The use of a dedicated machine (virtual or otherwise) for
running shadowlands would reduce the potential for malicious actors to
attack the program directly.  Providing signed releases for the
installer and shadowlands-core would also help with verifying the
integrity of the code before it is run.

## Recommendations for the Shadowlands Installer and ÐApp

Neither the installer nor the ÐApp (`sloader.shadowlands.eth`) present
any immediate security risks.  Their surface area is sufficiently
small enough to leave little room for exploit.  Calling python code
from within a bash script to kick off the installation is not a
standard means of package management but it also does not present any
immediate security concerns so long as the integrity of the script can
be verified after downloading.

## Recommendations for shadowlands-core

`shadowlands-core` presented a few minor risks when audited.  These
issues were mostly concerning best practices and can be easily
remedied with small code changes.

### Library Updates and Recommendations (Low Severity)

All of the libraries in the `shadowlands-core` requirements were
checked for known vulnerabilities and none were found.  Several of the
libraries were slightly behind on versions and should be updated to
include the latest fixes for those projects.  Furthermore, the
`kayagoban/asciimatics` fork should regularly merge in security and
bug fixes from the upstream project.

#### Outdated Libraries and Recommended Versions

- `certifi` (2018.11.29 or later)
- `ECPy` (0.10.0 or later)
- `eth-abi` (1.2.0 or later)
- `eth-typing` (2.0.0 or later)
- `eth-utils` (1.3.0 or later)
- `ethereum` (2.3.2 or later)
- `future` (0.17.1 or later)
- `ledgerblue` (0.1.21 or later)
- `numpy` (1.15.4 or later)
- `parsimonious` (0.8.1 or later)
- `Pillow` (5.3.0 or later)
- `py-solc` (3.2.0 or later)
- `pycryptodome` (3.7.2 or later)
- `pycryptodomex` (3.7.2 or later)
- `pyfiglet` (0.7.5 or later)
- `requests` (2.20.1 or later)
- `rlp` (1.0.3 or later)
- `urllib3` (1.24.1 or later)
- `web3` (4.8.2 or later)
- `websockets` (7.0 or later)

### Use of yaml.load (Medium Severity)

`sl_config.py` calls `yaml.load` at line 53 on an arbitrary file.  The
PyYAML load function allows the ability to construct arbitrary Python
objects.  This could could allow an attacker to craft a malicious
`shadowlands_conf` file.

Example exploit (truncated):

```
>>> import yaml
>>> yaml.load('!!python/object/apply:os.system ["id"]')
uid=1000(cmhobbs) gid=1000(cmhobbs) groups=1000(cmhobbs),20(dialout)...
```

In order to resolve this issue, the `yaml.safe_load` function should
be called instead.  See the
[PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
for more information.

### Creation of temp directories (Low Severity)

In `dapp_browser.py` on line 88, a hardcoded path is specified.  While
the path provided is likely benign, it could theoretically open the
program up to time of check to time of use attacks or other race
conditions.  Look into the use of `tempfile` in Python stdlib for
options to resolve this issue.
