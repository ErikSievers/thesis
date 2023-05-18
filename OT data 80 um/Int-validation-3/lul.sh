for filename in *.tif; do
    new_filename=$(echo "$filename" | sed -E 's/([A-Za-z]+_)([0-9]+)(_.*\.tif)/\1\2_000\3/')
    mv "$filename" "$new_filename"
done