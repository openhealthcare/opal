# Opal Management Commands

Opal ships with a number of Django management commands which can be invoked with
`python manage.py command`.

## create_random_data

Creates patients with randomised data.

*Arguments*:

* `--number` - The number of patients to create. Defaults to 100.

```bash
python manage.py create_random_data --number 3000
```

## create_singletons

Creates any subrecord singletons which are missing. This is useful when
creating a new singleton subrecord to backfill existing patients or episodes.

Will not create anything if singletons exist, so safe to be run as part of e.g. a
deployment script.

```bash
python manage.py create_singletons
```

## delete_all_lookuplists

Deletes all instances of lookuplist and synonym entries.

```bash
python manage.py delete_all_lookuplists
```

## detect_duplicates

Examines patients in the system and looks for possible duplicates. Prints a report
of patients with matching names, dates of birth or hospital numbers.

```bash
python manage.py detect_duplicates
```

## dump_lookup_lists

*Arguments*:

* `--many-files` - write lookuplists to separate files instead of printing them to stdout.

Prints current lookuplist and synonym values as JSON to stdout. Suitable to be used
as the input to `load_lookup_lists`

```bash
python manage.py dump_lookup_lists
```


## load_lookup_lists

Load lookuplists and synonym values.

*Arguments*:

* `--file` - Load one specific file only.

By default this command will look in `./yourapp/data/lookuplists.json` as well as in
`./yourapp/data/` for any files with a name matching the API name of a lookuplist
(e.g. `./yourapp/data/conditions.json`)

```bash
python manage.py load_lookup_lists
```
