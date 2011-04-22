%define _requires_exceptions libstlport_gcc.so

Name:           libreoffice-voikko
Version:        3.2
Release:        %mkrel 1
Summary:        Finnish spellchecker and hyphenator extension for LibreOffice
Group:          Office
License:        GPLv3+
URL:            http://voikko.sourceforge.net/
# The usual format of stable release URLs
Source0:        http://downloads.sourceforge.net/voikko/%{name}-%{version}.tar.gz
# The usual format of test release URLs
#Source0:        http://www.puimula.org/htp/testing/%{name}-%{version}rc2.tar.gz
BuildRequires:    libreoffice-devel >= 3.2.99
BuildRequires:    libvoikko-devel >= 2.1
Requires:         libreoffice-core >= 3.2.99
Requires:	locales-fi
# Rpmbuild only detects libvoikko.so.1 automatically, which is
# too general for openoffice.org-voikko.
Requires:         libvoikko >= 2.1
Obsoletes:	openoffice.org-voikko < 3.3

%define libo %{_libdir}/ooo
%define libo_sdk %{libo}/basis3.3/sdk
# The location of the installed extension. Apparently the directory name must
# end with .uno.pkg or unopkg will fail.
%define voikkoext %{libo}/share/extensions/voikko.uno.pkg

%description
This package contains a Finnish spell-checking and hyphenation component for
LibreOffice. The actual spell-checking and hyphenation functionality is
provided by the Voikko library.


%prep
%setup -q

%build
. %{libo_sdk}/setsdkenv_unix.sh
%make OPT_FLAGS="%optflags" STLPORTLIB=

%install
rm -rf $RPM_BUILD_ROOT
. %{libo_sdk}/setsdkenv_unix.sh
%make install-unpacked DESTDIR=%{buildroot}%{voikkoext} OPT_FLAGS="%optflags"
# Set the library executable so debuginfo can be extracted.
chmod +x %{buildroot}%{voikkoext}/voikko.so


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{voikkoext}
%doc ChangeLog COPYING README


