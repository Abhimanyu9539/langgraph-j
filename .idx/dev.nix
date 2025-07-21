# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"
  
  # Use https://search.nixos.org/packages to find packages
  packages = [
    # Python 3.11 for better compatibility
    pkgs.python311
    # UV - Fast Python package manager
    pkgs.uv
    # Build tools that Python packages might need
    pkgs.gcc
    pkgs.pkg-config
    pkgs.git
    # Optional: Add other system tools you might need
    # pkgs.nodejs_20
    # pkgs.sqlite
  ];
  
  # Sets environment variables in the workspace
  env = {
    # Let UV manage the Python environment
    UV_PYTHON = "python3.11";
    # UV cache directory
    UV_CACHE_DIR = ".uv-cache";
  };
  
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # Python extensions
      "ms-python.python"
      "ms-python.vscode-pylance"
      # Optional: Add other useful extensions
      # "ms-python.black-formatter"
      # "ms-python.isort"
    ];
    
    # Enable previews
    previews = {
      enable = true;
      previews = {
        # Add web previews here if you build web apps
        # web = {
        #   command = ["python" "main.py"];
        #   manager = "web";
        #   env = {
        #     PORT = "$PORT";
        #   };
        # };
      };
    };
    
    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        # Initialize UV project
        init-uv-project = "uv init --python 3.11";
        # Create pyproject.toml if it doesn't exist
        create-pyproject = ''
          if [ ! -f pyproject.toml ]; then
            cat > pyproject.toml << 'EOF'
[project]
name = "my-project"
version = "0.1.0"
description = "A Python project managed with UV"
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
dependencies = []
requires-python = ">=3.11"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = []
EOF
          fi
        '';
        # Open default files
        default.openFiles = [ ".idx/dev.nix" "pyproject.toml" "README.md" ];
      };
      
      # Runs when the workspace is (re)started
      onStart = {
        # Sync dependencies (creates .venv automatically)
        sync-deps = "uv sync";
        # Show UV status
        show-status = "echo 'UV Python environment ready! Use: uv add <package> to install packages'";
      };
    };
  };
}