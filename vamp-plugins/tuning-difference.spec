# Tag: Effect, Analyzer
# Type: Plugin, VAMP
# Category: Audio, Effect

Name: tuning-difference
Version: 1.0
Release: 1%{?dist}
Summary: Vamp plugin that estimates the tuning frequency of a recording
License: GLPv2	
URL: https://code.soundsoftware.ac.uk/projects/tuning-difference	

Vendor:       Audinux
Distribution: Audinux

Source0: https://code.soundsoftware.ac.uk/hg/tuning-difference/archive/tip.zip#/tuning-difference.zip

BuildRequires: gcc gcc-c++ make
BuildRequires: vamp-plugin-sdk-devel

%description
Vamp plugin that estimates the tuning frequency of a recording, by comparing
it to another recording of the same music whose tuning frequency is known.

%package -n vamp-%{name}
Summary: %{name} VAMP plugin

%description -n vamp-%{name}
%{description}

%prep
%autosetup -n %{name}-c0b78dcc08e6

sed -i -e "s/-Wall -Wextra.*/\$(VAMPCFLAGS)/g" Makefile.linux
sed -i -e "s/-std=c++11.*/\$(VAMPCCCFLAGS)/g" Makefile.linux
sed -i -e "s/-Wl,-Bstatic //g" Makefile.linux

%build

%set_build_flags

export VAMPCFLAGS="$CFLAGS -fPIC"
export VAMPCXXFLAGS="$CXXFLAGS -fPIC"

%make_build -j1 -f Makefile.linux

%install

install -m 755 -d %{buildroot}/%{_libdir}/vamp/
install -m 755 tuning-difference.so  %{buildroot}/%{_libdir}/vamp/
install -m 644 tuning-difference.cat %{buildroot}/%{_libdir}/vamp/
install -m 644 tuning-difference.n3  %{buildroot}/%{_libdir}/vamp/

%files -n vamp-%{name}
%license COPYING
%doc README.md
%{_libdir}/vamp/tuning-difference.*

%changelog
* Sat Jan 08 2022 Yann Collette <ycollette.nospam@free.fr> - 1.0-1
- Initial spec file
