#!/bin/bash
# GNOME Markdown QuickLook - One-line installer
# Usage: curl -fsSL https://raw.githubusercontent.com/noboomu/gnome-markdown-quicklook/main/install.sh | bash

set -e

# Colors and symbols
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

readonly CHECK='✓'
readonly CROSS='✗'
readonly ARROW='→'
readonly STAR='★'

# Project info
readonly PROJECT_NAME="GNOME Markdown QuickLook"
readonly PROJECT_VERSION="1.0.0"
readonly PROJECT_URL="https://github.com/noboomu/gnome-markdown-ql"

# Installation paths
if [[ $EUID -eq 0 ]]; then
    readonly INSTALL_MODE="system"
    readonly SUSHI_DIR="/usr/share/sushi/viewers"
    readonly CONVERTER_DIR="/usr/local/bin"
    readonly MIME_DIR="/usr/share/mime/packages"
else
    readonly INSTALL_MODE="user"
    readonly SUSHI_DIR="$HOME/.local/share/sushi/viewers"
    readonly CONVERTER_DIR="$HOME/.local/bin"
    readonly MIME_DIR="$HOME/.local/share/mime/packages"
fi

# Utility functions
print_header() {
    echo -e "${PURPLE}"
    echo "╭─────────────────────────────────────────────────────────────╮"
    echo "│                                                             │"
    echo "│  ${STAR} ${WHITE}GNOME Markdown QuickLook${PURPLE} ${STAR}                            │"
    echo "│                                                             │"
    echo "│  ${WHITE}Beautiful markdown previews for GNOME${PURPLE}                   │"
    echo "│  ${CYAN}Press Space in Nautilus to preview .md files${PURPLE}            │"
    echo "│                                                             │"
    echo "╰─────────────────────────────────────────────────────────────╯"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}${ARROW}${NC} $1"
}

print_success() {
    echo -e "${GREEN}${CHECK}${NC} $1"
}

print_error() {
    echo -e "${RED}${CROSS}${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_info() {
    echo -e "${CYAN}i${NC} $1"
}

spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

check_dependencies() {
    print_step "Checking system dependencies..."

    local missing_deps=()

    # Check GNOME Sushi
    if ! command -v sushi &> /dev/null; then
        missing_deps+=("gnome-sushi")
    fi

    # Check WebKit2GTK
    if ! pkg-config --exists webkit2gtk-4.1 && ! pkg-config --exists webkit2gtk-4.0; then
        missing_deps+=("libwebkit2gtk-4.1-dev")
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_info "Install with: ${YELLOW}sudo apt install ${missing_deps[*]}${NC}"
        exit 1
    fi

    print_success "All system dependencies found"
}

setup_python_env() {
    print_step "Setting up Python environment..."

    if command -v uv &> /dev/null; then
        print_info "Using ${CYAN}uv${NC} for dependency management"

        # Create temporary project for dependencies
        local temp_dir=$(mktemp -d)
        cd "$temp_dir"

        cat > pyproject.toml << 'EOF'
[project]
name = "gnome-markdown-quicklook-installer"
version = "0.1.0"
dependencies = [
    "markdown>=3.5",
    "pygments>=2.15",
    "pymdown-extensions>=10.0",
    "commonmark>=0.9.1",
    "markdown-it-py>=3.0.0",
    "python-markdown-math>=0.8",
]
EOF

        uv sync --quiet &
        spinner $!
        print_success "Python dependencies installed"

        # Export the environment for the converter script
        export UV_PROJECT_ROOT="$temp_dir"
        cd - > /dev/null
    else
        print_info "Installing Python dependencies with pip..."
        uv pip install   --quiet \
            'markdown>=3.5' \
            'pygments>=2.15' \
            'pymdown-extensions>=10.0' \
            'commonmark>=0.9.1' \
            'markdown-it-py>=3.0.0' \
            'python-markdown-math>=0.8' &
        spinner $!
        print_success "Python dependencies installed"
    fi
}

download_files() {
    print_step "Downloading project files..."

    local temp_dir=$(mktemp -d)
    cd "$temp_dir"

    # Download main files
    curl -fsSL "${PROJECT_URL}/raw/main/src/gnome_markdown_quicklook/converter.py" -o converter.py &
    local dl1_pid=$!

    curl -fsSL "${PROJECT_URL}/raw/main/src/sushi-viewers/markdown.js" -o markdown.js &
    local dl2_pid=$!

    wait $dl1_pid $dl2_pid

    if [[ ! -f converter.py || ! -f markdown.js ]]; then
        print_error "Failed to download project files"
        exit 1
    fi

    print_success "Project files downloaded"

    # Export for use in installation
    export TEMP_FILES_DIR="$temp_dir"
}

install_files() {
    print_step "Installing extension files..."

    # Create directories
    mkdir -p "$SUSHI_DIR" "$CONVERTER_DIR" "$MIME_DIR"

    # Install converter
    cp "$TEMP_FILES_DIR/converter.py" "$CONVERTER_DIR/sushi-markdown-converter"
    chmod +x "$CONVERTER_DIR/sushi-markdown-converter"

    # Install Sushi viewer
    cp "$TEMP_FILES_DIR/markdown.js" "$SUSHI_DIR/"

    print_success "Extension files installed"
}

setup_mime_types() {
    print_step "Configuring file associations..."

    cat > "$MIME_DIR/markdown.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="text/markdown">
    <comment>Markdown document</comment>
    <glob pattern="*.md"/>
    <glob pattern="*.markdown"/>
    <glob pattern="*.mdown"/>
    <glob pattern="*.mkd"/>
    <glob pattern="*.mkdn"/>
  </mime-type>
  <mime-type type="text/x-markdown">
    <comment>Markdown document</comment>
    <glob pattern="*.md"/>
    <glob pattern="*.markdown"/>
  </mime-type>
</mime-info>
EOF

    # Update MIME database
    if [[ "$INSTALL_MODE" == "system" ]]; then
        update-mime-database /usr/share/mime &> /dev/null
    else
        update-mime-database ~/.local/share/mime &> /dev/null
    fi

    print_success "File associations configured"
}

finalize_installation() {
    print_step "Finalizing installation..."

    # Restart Sushi
    pkill -f sushi 2>/dev/null || true
    sleep 1

    # Add to PATH if needed (user install)
    if [[ "$INSTALL_MODE" == "user" && ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        print_info "Added ${CYAN}~/.local/bin${NC} to PATH in ~/.bashrc"
    fi

    print_success "Installation finalized"
}

print_completion() {
    echo
    echo -e "${GREEN}╭─────────────────────────────────────────────────────────────╮"
    echo -e "│  ${CHECK} Installation completed successfully!                     │"
    echo -e "╰─────────────────────────────────────────────────────────────╯${NC}"
    echo
    print_info "Quick Start:"
    echo -e "  ${CYAN}1.${NC} Open ${YELLOW}Nautilus${NC} (GNOME Files)"
    echo -e "  ${CYAN}2.${NC} Select any ${YELLOW}.md${NC} file"
    echo -e "  ${CYAN}3.${NC} Press ${YELLOW}Space${NC} for preview"
    echo -e "  ${CYAN}4.${NC} Press ${YELLOW}Escape${NC} to close"
    echo
    print_info "Supported formats: ${CYAN}.md .markdown .mdown .mkd .mkdn${NC}"
    print_info "Features: ${CYAN}Syntax highlighting, tables, math, themes${NC}"
    echo
    print_info "Documentation: ${BLUE}${PROJECT_URL}${NC}"

    if [[ "$INSTALL_MODE" == "user" ]]; then
        echo
        print_warning "Run ${YELLOW}source ~/.bashrc${NC} or restart terminal for PATH updates"
    fi
}

# Main installation flow
main() {
    clear
    print_header

    echo -e "${WHITE}Installing to:${NC} ${CYAN}$INSTALL_MODE${NC} (${SUSHI_DIR})"
    echo

    check_dependencies
    setup_python_env
    download_files
    install_files
    setup_mime_types
    finalize_installation

    print_completion
}

# Run installer
main "$@"
