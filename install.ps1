# Determine the appropriate arch to install
if ($env:PLATFORM -eq "x86") {
    $arch = "i686"
    $ngrok_archive = "ngrok-stable-windows-386.zip"
}
else {
    $arch = "x86_64"
    $ngrok_archive = "ngrok-stable-windows-amd64.zip"
}


# Install ngrok
Start-FileDownload "https://bin.equinox.io/c/4VmDzA7iaHb/$ngrok_archive"
unzip "$ngrok_archive"
rm "$ngrok_archive"


$rust_version = $env:RUST_VERSION
$rust_install = "rust-$rust_version-$arch-pc-windows-gnu.msi"

# Download Rust installer
Start-FileDownload "https://static.rust-lang.org/dist/$rust_install" -FileName $rust_install


# Install Rust
Start-Process -FilePath msiexec -ArgumentList /i, $rust_install, /quiet, INSTALLDIR="C:\Rust" -Wait

# Add Rust to path
$env:Path = $env:Path + ";C:\Rust\bin"

"Rust version:"
""
rustc -vV
""
""

"Cargo version:"
""
cargo -V
""
""
