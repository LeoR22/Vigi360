# scripts/bootstrap.sh
set -e
mkdir -p app/data/{raw,processed,models,logs}
python -m app.services.etl --fetch
python -m app.services.features --build
python -m app.services.train --fit
