#!/bin/bash
# Update all admin pages to use new navigation

for file in admin-*.html; do
    if [[ "$file" == "admin-login.html" ]]; then
        continue
    fi
    
    echo "Processing $file..."
    
    # Add admin-nav.js script if not present
    if ! grep -q "admin-nav.js" "$file"; then
        sed -i 's|<head>|<head>\n    <script src="/admin-nav.js"></script>|' "$file"
        echo "  - Added admin-nav.js to $file"
    fi
    
    # Remove old navigation styles that conflict
    if grep -q "\.header {" "$file"; then
        echo "  - Navigation will be replaced by sidebar in $file"
    fi
done

echo "Done!"
