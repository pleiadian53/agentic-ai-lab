#!/bin/bash
# Switch from Anaconda to Miniforge as primary conda installation
# Usage: ./scripts/install/switch-to-miniforge.sh

set -e

echo "🔄 Switching to Miniforge/Mamba"
echo "================================"
echo ""

# Backup current .zshrc
echo "📋 Backing up ~/.zshrc to ~/.zshrc.backup..."
cp ~/.zshrc ~/.zshrc.backup
echo "✅ Backup created at ~/.zshrc.backup"
echo ""

# Remove Anaconda conda initialization blocks
echo "🗑️  Removing Anaconda initialization from ~/.zshrc..."
# Create a temporary file without conda blocks
awk '
/^# >>> conda initialize >>>/ {
    in_block=1
    block=""
}
in_block {
    block = block $0 "\n"
    if (/^# <<< conda initialize <<</) {
        # Check if this is Anaconda block
        if (block !~ /anaconda3/) {
            # Keep non-Anaconda blocks (miniforge)
            printf "%s", block
        }
        in_block=0
        block=""
    }
    next
}
!in_block {
    print
}
' ~/.zshrc > ~/.zshrc.tmp

mv ~/.zshrc.tmp ~/.zshrc
echo "✅ Anaconda initialization removed"
echo ""

# Initialize Miniforge
echo "🔧 Initializing Miniforge..."
/Users/pleiadian53/miniforge3-new/bin/conda init zsh
echo "✅ Miniforge initialized"
echo ""

# Initialize mamba
echo "🔧 Initializing mamba..."
/Users/pleiadian53/miniforge3-new/bin/mamba init
echo "✅ Mamba initialized"
echo ""

echo "🎉 Switch Complete!"
echo ""
echo "⚠️  IMPORTANT: You must restart your terminal for changes to take effect"
echo ""
echo "After restarting:"
echo "  1. Run: mamba --version  (should show mamba version)"
echo "  2. Run: which conda  (should point to miniforge3-new)"
echo "  3. Run: conda env list  (should show miniforge environments)"
echo "  4. Recreate agentic-ai environment:"
echo "     cd /Users/pleiadian53/work/agentic-ai-public"
echo "     mamba env create -f environment.yml"
echo "     mamba activate agentic-ai"
echo ""
echo "💡 Your old .zshrc is backed up at ~/.zshrc.backup"
echo ""
