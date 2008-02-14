nmexecdir = $(bindir)
nmexec_DATA = nmcli

nmsupportdir = $(datadir)/nm
nmsupport_DATA =       \
	i18n.py	       \
	nmcommand.py   \
	nmmain.py      \
	nmformat.py    \
	nmtalk.py      \
	nm.py          \
	nmap.py        \
	nmdevice.py    \
	nmip4config.py \
	nmobject.py    \
	nmsettings.py  \
	nmvpn.py

nmcmdsdir = $(nmsupportdir)/commands
nmcmds_DATA =                    \
	nmapcmds.py              \
	nmcmds.py                \
	nmconnectioncmds.py      \
	nmdevicecmds.py          \
	nmvpncmds.py             \
	nmwireddevicecmds.py     \
	nmwirelessdevicecmds.py

EXTRA_DIST = $(nmsupport_DATA) $(nmcmds_DATA)

install-exec-hook:
	chmod 0755 $(DESTDIR)$(nmexecdir)/$(nmexec_DATA)
