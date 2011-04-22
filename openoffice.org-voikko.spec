%define srcname	openoffice.org
%define ooname	%srcname
%define unopkg	%{_libdir}/%{ooodir}/program/unopkg

%define ooo_version %(rpm -q --qf '%%{epoch}:%%{version}' %{ooname}-devel 2>/dev/null)
%define ooodir	ooo

%define binname	%{ooname}-voikko
%define name	%{srcname}-voikko

%define version	3.1
%define rel	4

%define unopkgname	voikko.oxt

Summary:	Finnish spellchecker and hyphenator for OpenOffice.org
Name:		%name
Version:	%version
Release:	%mkrel %rel
License:	GPL
Group:		Office
URL:            http://voikko.sourceforge.net/
Source:         http://downloads.sourceforge.net/voikko/%name-%version.tar.gz
BuildRoot:	%{_tmppath}/%{name}-root
BuildRequires:	%ooname-devel
BuildRequires:	zip
BuildRequires:	voikko-devel >= 2.1
Requires:	locales-fi
# Binaries are hidden inside a zip, so automatic dependencies won't work
Requires:	%{mklibname voikko 1}
Requires:	voikko-dictionary
Requires:	%ooname-common = %ooo_version
Requires(pre):	%ooname-common = %ooo_version
Requires(post):	%ooname-common = %ooo_version
Requires(preun):	%ooname-common = %ooo_version
%ifarch x86_64
Obsoletes:	openoffice.org64-voikko
%endif

%description
Finnish spellchecker and hyphenator component for OpenOffice.org.

Usually Voikko is automatically activated after the installation. If
that won't happen, you can manually activate it from the Writing
Aids section of the OpenOffice.org options.

%prep
%setup -q

%build
. %{_libdir}/%{ooodir}/basis-link/sdk/setsdkenv_unix.sh

# (Anssi 09/2008) Our current OOo has some broken make variables.
# Some devel library symlinks also appear to be nowhere.
%make OPT_FLAGS="%optflags" all

%install
rm -rf %{buildroot}

install -d -m755 %{buildroot}%{_libdir}/%{binname}
install -m644 build/%{unopkgname} %{buildroot}%{_libdir}/%{binname}

%clean
rm -rf %{buildroot}

%pre
if ! [ -x %unopkg ]; then
	echo "ERROR: Compatible version of OpenOffice.org is not installed, aborting the"
	echo "       installation or upgrade of %{binname}!"
	exit 1
fi

# (anssi) Map of triggercity:
# Note that installation of voikko implies automatic uninstallation of old
# versions for the compatible instance of openoffice.org.
# Upgrade of openoffice.org-voikko:
# - TRIGGERUN of old version is run, but $1 = 1 and $2 = 1, thus no action is
#   taken
# - POSTTRANS of new version installs new version
# Upgrade of openoffice.org to a compatible version:
# - TRIGGERUN is run, but $1 = 1 and $2 = 1, thus no action is taken
# Upgrade of openoffice.org and openoffice.org-voikko to a compatible version:
# - TRIGGERUN of old version is run, but $1 = 1 and $2 = 1, thus no action is
#   taken
# - TRIGGERUN of old version is run again, but $1 = 1 and $2 = 1, thus no
#   action is taken
# - POSTTRANS of new version installs new version
# Upgrade of openoffice.org and openoffice.org-voikko to an incompatible
# version:
# - TRIGGERIN of old version removes old version
# - TRIGGERUN of old version is run, but $1 = 1 and $2 = 1, thus no action is
#   taken
# - openoffice.org files are replaced with new versions
# - POSTTRANS of new version installs new version
# Upgrade of openoffice.org to an incompatible version, with
# openoffice.org-voikko being removed:
# - TRIGGERIN removes voikko
# - TRIGGERUN is run, but $1 = 1 and $2 = 1, thus no action is taken
# - openoffice.org files are replaced with new versions
# Downgrade of openoffice.org-voikko:
# - TRIGGERUN of new version is run, but $1 = 1 and $2 = 1, thus no action is
#   taken
# - POSTTRANS of old version installs old version
# Removal of openoffice.org-voikko:
# - TRIGGERUN removes voikko as $1 = 0 and $2 = 1
# Removal of openoffice.org and openoffice.org-voikko
# - TRIGGERUN removes voikko as $1 = 1 and $2 = 0
# - openoffice.org files are removed
#

# Posttrans is used instead of post to allow upgrade from old
# openoffice.org-voikko with preun that would remove the new version installed
# in post, without adding triggers for that.
%posttrans
if [ -x %unopkg ]; then
	# unopkg writes into $HOME
	TMP_HOME=$(mktemp -t -d %{binname}.XXXXXX) || exit 1
	export HOME=$TMP_HOME
	# make sure no other version is installed
	for pkg in $(%unopkg list --shared 2>/dev/null | sed -ne 's/^Identifier: \(org.puimula.ooovoikko\)/\1/p'); do
		%unopkg remove --shared $pkg
	# empty line due to macro expansion
	done
	%unopkg add --shared %{_libdir}/%{binname}/%{unopkgname}
	rm -rf $TMP_HOME
fi

%triggerun -- %ooname-common = %ooo_version
# Preun script cannot be used for this as rpm doesn't honor Requires(preun),
# but just removes OOo before preun would be run.
# Executed just before OOo or voikko is being completely removed. Does not run
# on normal upgrades.
if [ $1 -eq 0 ] || [ $2 -eq 0 ]; then
	if [ -x %unopkg ]; then
		# unopkg writes into $HOME
		TMP_HOME=$(mktemp -t -d %{binname}.XXXXXX) || exit 1
		export HOME=$TMP_HOME
		%unopkg remove --shared org.puimula.ooovoikko
		# get rid of cache:
		%unopkg list --shared &>/dev/null
		rm -rf $TMP_HOME
	fi
fi
true

%triggerin -- %ooname-common > %ooo_version
# Executed just before OOo is being upgraded to an incompatible version.
# Cannot be in preun for the same reason as above triggerun.
if [ -x %unopkg ]; then
	# unopkg writes into $HOME
	TMP_HOME=$(mktemp -t -d %{binname}.XXXXXX) || exit 1
	export HOME=$TMP_HOME
	%unopkg remove --shared org.puimula.ooovoikko
	# get rid of cache:
	%unopkg list --shared &>/dev/null
	rm -rf $TMP_HOME
fi

%files
%defattr(-,root,root)
%doc README ChangeLog
%{_libdir}/%{binname}
