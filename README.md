# SD1.5 Daily Gallery

CPU 전용 Stable Diffusion 1.5 배치 프로젝트입니다. `subjects.json`에 정리된 검증 프롬프트 중 매일 5개를 무작위로 선택하고 (후보가 5개 이상이면 중복 없이 선택하며, 부족하면 중복 허용), 각 이미지에 독립적인 랜덤 시드를 사용합니다.

## 수동 실행

```bash
docker compose build
docker compose run --rm generator
```

결과는 `output/image-1.webp`부터 `image-5.webp`, 메타데이터는 `output/latest.json`에 저장됩니다. 날짜별 사본은 `output/archive/YYYY-MM-DD/`에 남습니다.

## 매일 오전 8시 cron

프로젝트를 `/home/darek123/python_projects/sd15-daily-gallery`에 둔 경우:

```cron
0 8 * * * /bin/bash /home/darek123/python_projects/sd15-daily-gallery/scripts/run_daily.sh
```

Widget Board와 이 프로젝트를 같은 `python_projects` 아래에 두면 Widget Board가 `../sd15-daily-gallery/output`을 읽습니다.


## Preservation implementation notes

The CPU generator writes current images, metadata and date archives. Selection is without replacement only when the subject pool is large enough; the existing fallback samples with replacement. Widget Board can read the output directory. The existing scheduled job was not stopped, changed or re-run.

## Maintenance status

Development and maintenance are discontinued. This is a preservation snapshot, not a new release or feature-development plan. Running services and scheduled jobs are not automatically shut down by this status.

This repository is intended for Private preservation. Public release requires a separate review and approval. See PRESERVATION.md for excluded material and verification limits.
