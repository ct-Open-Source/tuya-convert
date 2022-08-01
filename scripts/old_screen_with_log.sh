# Run screen with a custom .screenrc that defines the name of "logfile"

screen_minor=${1}
screen_logfile_name=${2}
screen_other_options=${@:3}

if [ "$screen_minor" -gt 5 ]; then
	echo "Info: you have the modern enough version" \
             "to use the \"-Logfile\" flag of \"screen\""
elif [ "$screen_minor" -eq 5 ]; then
	screen_with_log="sudo screen -L"
else
	screen_with_log="sudo screen -L -t"
fi

echo "logfile ${screen_logfile_name}" > ${screen_logfile_name}.screenrc

${screen_with_log} ${screen_logfile_name} \
    -c ${screen_logfile_name}.screenrc ${screen_other_options}

rm ${screen_logfile_name}.screenrc
