for filename in *.tif; do
    new_filename=$(echo "$filename" | awk -F '_' 'BEGIN{OFS=FS}{printf "%s_%03d_%s.tif\n", $1, $2, $3}')
    mv "$filename" "$new_filename"
done