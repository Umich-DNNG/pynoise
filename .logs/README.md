# Guide for Logs

Since many changes to the settings and different types of analyses can be completed during one runtime, the user may desire to keep track of all these changes/analyses. These logs will keep track of these changes in a condensed format.

## Log Naming Scheme

Logs are named based on time stamps. The formatting is as follows:

YYYY-MM-DD@HH:MM:SS.log

## Log Message Conventions

Each log message will also include a timestamp in the same formatting - the only difference is the inclusion of whitespace around the @ symbol. The timestamp is then followed by a whitespace padded -, and the output message is then stated.

## Types of Log Messages

The following operations made during runtime will be recorded by the log:

* Settings were imported from a file.
* New settings were created.
* Current settings were modified in any way.
* Performing any modular analysis on the data (time differences, histogram plotting, etc.)
* Running an entire method (RossiAlpha)
* Overwriting previously stored analysis data.
* Overwriting settings files at the end of runtime.
* Creating a new settings fil eat the end of runtime.
* Discarded the current settings at the end of runtime.

It should be assumed that anything not in this list will not be included in log files.