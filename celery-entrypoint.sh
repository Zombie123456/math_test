#!/bin/bash
celery -A mathtest worker -l info -Q others -n others@%h &
celery -A mathtest worker -Q delete_expire -n delete_expire@%h &
celery -A mathtest beat -l info --pidfile=
