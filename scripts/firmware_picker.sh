#!/bin/bash

MAGIC=`printf "\xe9"`

while true; do
	echo
	echo "Available options:"
	echo "  0) return to stock"
	index=0
	for file in ../files/*.bin; do
		# skip null glob
		[[ -e $file ]] || continue
		# get short name
		filename=`basename "$file"`
		# skip files too large or too small
		filesize=`stat -c%s "$file"`
		[[ "$filesize" -gt 0x1000 && "$filesize" -le 0x80000 ]] || continue
		# skip files without magic byte
		[[ `head -c 1 "$file"` == $MAGIC ]] || continue
		echo "  $((++index))) flash $filename"
		options[$index]="$filename"
	done
	echo "  q) quit; do nothing"
	echo -n "Please select 0-$index: "
	while true; do
		read -n 1 -r
		echo
		if [[ "$REPLY" =~ ^[0-9]$ && "$REPLY" -ge 0 && "$REPLY" -le $index ]]; then
			break
		fi
		if [[ "$REPLY" =~ ^[Qq]$ ]]; then
			echo "Leaving device as is..."
			return
		fi
		echo -n "Invalid selection, please select 0-$index: "
	done

	if [[ "$REPLY" == 0 ]]; then
		if curl -s http://10.42.42.42/undo; then
			echo "Disconnect the device to prevent it from repeating the upgrade"
			echo "You will need to put the device back into pairing mode and register to use again"
		else
			echo "Could not reach the device!"
		fi
		break
	fi

	selection="${options[$REPLY]}"
	read -p "Are you sure you want to flash $selection? This is the point of no return [y/N] " -n 1 -r
	echo
	[[ "$REPLY" =~ ^[Yy]$ ]] || continue

	echo "Attempting to flash $selection, this may take a few seconds..."
	RESULT=`curl -s "http://10.42.42.42/flash?url=http://10.42.42.1/files/$selection"` ||
	echo "Could not reach the device!"

	echo "$RESULT"
	if [[ "$RESULT" =~ failed ]]; then
		read -p "Do you want to try something else? [y/N] " -n 1 -r
		echo
		[[ "$REPLY" =~ ^[Yy]$ ]] || break
	else
		break
	fi
done

