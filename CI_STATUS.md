# CI failed

Commit: `a5bdfd842699db88fa8e233eaa1a8493ae01db7f`

```text
Collecting prometheus-client>=0.8.0 (from flower==2.0.1->-r requirements.txt (line 90))
  Downloading prometheus_client-0.25.0-py3-none-any.whl.metadata (2.1 kB)
Collecting humanize (from flower==2.0.1->-r requirements.txt (line 90))
  Downloading humanize-4.16.0-py3-none-any.whl.metadata (8.0 kB)
Collecting limits>=2.3 (from slowapi==0.1.9->-r requirements.txt (line 91))
  Downloading limits-5.8.0-py3-none-any.whl.metadata (10 kB)
Collecting chardet (from reportlab==4.2.5->-r requirements.txt (line 92))
  Downloading chardet-7.4.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (9.4 kB)
Collecting et-xmlfile (from openpyxl==3.1.5->-r requirements.txt (line 93))
  Downloading et_xmlfile-2.0.0-py3-none-any.whl.metadata (2.7 kB)
Collecting amqp<6.0.0,>=5.1.1 (from kombu<6.0,>=5.3.4->celery==5.4.0->-r requirements.txt (line 89))
  Downloading amqp-5.3.1-py3-none-any.whl.metadata (8.9 kB)
Collecting prompt-toolkit>=3.0.36 (from click-repl>=0.2.0->celery==5.4.0->-r requirements.txt (line 89))
  Downloading prompt_toolkit-3.0.52-py3-none-any.whl.metadata (6.4 kB)
Collecting deprecated>=1.2 (from limits>=2.3->slowapi==0.1.9->-r requirements.txt (line 91))
  Downloading deprecated-1.3.1-py2.py3-none-any.whl.metadata (5.9 kB)
Collecting wrapt<3,>=1.10 (from deprecated>=1.2->limits>=2.3->slowapi==0.1.9->-r requirements.txt (line 91))
  Downloading wrapt-2.2.2-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (7.4 kB)
Collecting wcwidth (from prompt-toolkit>=3.0.36->click-repl>=0.2.0->celery==5.4.0->-r requirements.txt (line 89))
  Downloading wcwidth-0.8.2-py3-none-any.whl.metadata (43 kB)
Downloading aiohappyeyeballs-2.6.1-py3-none-any.whl (15 kB)
Downloading aiohttp-3.13.2-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (1.8 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.8/1.8 MB 156.4 MB/s  0:00:00
Downloading multidict-6.7.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (256 kB)
Downloading yarl-1.22.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (377 kB)
Downloading aiohttp_retry-2.9.1-py3-none-any.whl (10.0 kB)
Downloading aiosignal-1.4.0-py3-none-any.whl (7.5 kB)
Downloading alembic-1.17.2-py3-none-any.whl (248 kB)
Downloading annotated_doc-0.0.4-py3-none-any.whl (5.3 kB)
Downloading annotated_types-0.7.0-py3-none-any.whl (13 kB)
Downloading anyio-4.12.0-py3-none-any.whl (113 kB)
Downloading attrs-25.4.0-py3-none-any.whl (67 kB)
Downloading bcrypt-5.0.0-cp39-abi3-manylinux_2_34_x86_64.whl (278 kB)
Downloading cachetools-6.2.2-py3-none-any.whl (11 kB)
Downloading certifi-2025.11.12-py3-none-any.whl (159 kB)
Downloading cffi-2.0.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (219 kB)
Downloading charset_normalizer-3.4.4-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (153 kB)
Downloading click-8.3.1-py3-none-any.whl (108 kB)
Downloading croniter-6.0.0-py2.py3-none-any.whl (25 kB)
Downloading cryptography-46.0.3-cp311-abi3-manylinux_2_34_x86_64.whl (4.5 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.5/4.5 MB 228.6 MB/s  0:00:00
Downloading dnspython-2.8.0-py3-none-any.whl (331 kB)
Downloading ecdsa-0.19.1-py2.py3-none-any.whl (150 kB)
Downloading email_validator-2.3.0-py3-none-any.whl (35 kB)
Downloading fastapi-0.124.2-py3-none-any.whl (112 kB)
Downloading pydantic-2.12.5-py3-none-any.whl (463 kB)
Downloading starlette-0.50.0-py3-none-any.whl (74 kB)
Downloading frozenlist-1.8.0-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (242 kB)
Downloading geoip2-5.2.0-py3-none-any.whl (28 kB)
Downloading maxminddb-3.0.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (99 kB)
Downloading requests-2.32.5-py3-none-any.whl (64 kB)
Downloading idna-3.11-py3-none-any.whl (71 kB)
Downloading urllib3-2.6.2-py3-none-any.whl (131 kB)
Downloading google_api_core-2.28.1-py3-none-any.whl (173 kB)
Downloading google_auth-2.41.1-py2.py3-none-any.whl (221 kB)
Downloading googleapis_common_protos-1.72.0-py3-none-any.whl (297 kB)
Downloading proto_plus-1.26.1-py3-none-any.whl (50 kB)
Downloading protobuf-6.33.2-cp39-abi3-manylinux2014_x86_64.whl (323 kB)
Downloading rsa-4.9.1-py3-none-any.whl (34 kB)
Downloading google_api_python_client-2.187.0-py3-none-any.whl (14.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 14.6/14.6 MB 222.1 MB/s  0:00:00
Downloading google_auth_httplib2-0.2.1-py3-none-any.whl (9.5 kB)
Downloading httplib2-0.31.0-py3-none-any.whl (91 kB)
Downloading pyparsing-3.2.5-py3-none-any.whl (113 kB)
Downloading uritemplate-4.2.0-py3-none-any.whl (11 kB)
Downloading google_auth_oauthlib-1.2.3-py3-none-any.whl (19 kB)
Downloading greenlet-3.3.0-cp312-cp312-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl (609 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 609.9/609.9 kB 122.7 MB/s  0:00:00
Downloading h11-0.16.0-py3-none-any.whl (37 kB)
Downloading httpcore-1.0.9-py3-none-any.whl (78 kB)
Downloading httptools-0.7.1-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (517 kB)
Downloading httpx-0.28.1-py3-none-any.whl (73 kB)
Downloading iniconfig-2.3.0-py3-none-any.whl (7.5 kB)
Downloading mako-1.3.10-py3-none-any.whl (78 kB)
Downloading markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
Downloading oauthlib-3.3.1-py3-none-any.whl (160 kB)
Downloading packaging-25.0-py3-none-any.whl (66 kB)
Downloading passlib-1.7.4-py2.py3-none-any.whl (525 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 525.6/525.6 kB 100.9 MB/s  0:00:00
Downloading phonenumbers-9.0.20-py2.py3-none-any.whl (2.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.6/2.6 MB 161.7 MB/s  0:00:00
Downloading pluggy-1.6.0-py3-none-any.whl (20 kB)
Downloading propcache-0.4.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (221 kB)
Downloading psycopg2_binary-2.9.11-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (4.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.2/4.2 MB 296.3 MB/s  0:00:00
Downloading pyasn1-0.6.1-py3-none-any.whl (83 kB)
Downloading pyasn1_modules-0.4.2-py3-none-any.whl (181 kB)
Downloading pycparser-2.23-py3-none-any.whl (118 kB)
Downloading pydantic_settings-2.12.0-py3-none-any.whl (51 kB)
Downloading pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.1/2.1 MB 269.2 MB/s  0:00:00
Downloading pygments-2.19.2-py3-none-any.whl (1.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 156.8 MB/s  0:00:00
Downloading PyJWT-2.10.1-py3-none-any.whl (22 kB)
Downloading pytest-9.0.2-py3-none-any.whl (374 kB)
Downloading pytest_asyncio-1.3.0-py3-none-any.whl (15 kB)
Downloading python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
Downloading python_dotenv-1.2.1-py3-none-any.whl (21 kB)
Downloading python_http_client-3.3.7-py3-none-any.whl (8.4 kB)
Downloading python_jose-3.5.0-py2.py3-none-any.whl (34 kB)
Downloading python_multipart-0.0.20-py3-none-any.whl (24 kB)
Downloading pytz-2025.2-py2.py3-none-any.whl (509 kB)
Downloading pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (807 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 807.9/807.9 kB 164.5 MB/s  0:00:00
Downloading redis-7.1.0-py3-none-any.whl (354 kB)
Downloading requests_oauthlib-2.0.0-py2.py3-none-any.whl (24 kB)
Downloading rq-2.6.1-py3-none-any.whl (112 kB)
Downloading sendgrid-6.12.5-py3-none-any.whl (102 kB)
Downloading six-1.17.0-py2.py3-none-any.whl (11 kB)
Downloading sqlalchemy-2.0.45-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (3.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.3/3.3 MB 289.2 MB/s  0:00:00
Downloading twilio-9.8.8-py2.py3-none-any.whl (1.8 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.8/1.8 MB 259.4 MB/s  0:00:00
Downloading typing_inspection-0.4.2-py3-none-any.whl (14 kB)
Downloading typing_extensions-4.15.0-py3-none-any.whl (44 kB)
Downloading uvicorn-0.38.0-py3-none-any.whl (68 kB)
Downloading uvloop-0.22.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (4.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.4/4.4 MB 294.8 MB/s  0:00:00
Downloading watchfiles-1.1.1-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (456 kB)
Downloading websockets-15.0.1-cp312-cp312-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl (182 kB)
Downloading werkzeug-3.1.4-py3-none-any.whl (224 kB)
Downloading celery-5.4.0-py3-none-any.whl (425 kB)
Downloading flower-2.0.1-py2.py3-none-any.whl (383 kB)
Downloading slowapi-0.1.9-py3-none-any.whl (14 kB)
Downloading reportlab-4.2.5-py3-none-any.whl (1.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.9/1.9 MB 247.2 MB/s  0:00:00
Downloading openpyxl-3.1.5-py2.py3-none-any.whl (250 kB)
Downloading XlsxWriter-3.2.0-py3-none-any.whl (159 kB)
Downloading pillow-11.1.0-cp312-cp312-manylinux_2_28_x86_64.whl (4.5 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.5/4.5 MB 239.1 MB/s  0:00:00
Downloading billiard-4.2.4-py3-none-any.whl (87 kB)
Downloading kombu-5.6.2-py3-none-any.whl (214 kB)
Downloading vine-5.1.0-py3-none-any.whl (9.6 kB)
Downloading amqp-5.3.1-py3-none-any.whl (50 kB)
Downloading tornado-6.5.7-cp39-abi3-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (449 kB)
Downloading click_didyoumean-0.3.1-py3-none-any.whl (3.6 kB)
Downloading click_plugins-1.1.1.2-py2.py3-none-any.whl (11 kB)
Downloading click_repl-0.3.0-py3-none-any.whl (10 kB)
Downloading limits-5.8.0-py3-none-any.whl (60 kB)
Downloading deprecated-1.3.1-py2.py3-none-any.whl (11 kB)
Downloading wrapt-2.2.2-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (169 kB)
Downloading prometheus_client-0.25.0-py3-none-any.whl (64 kB)
Downloading prompt_toolkit-3.0.52-py3-none-any.whl (391 kB)
Downloading tzdata-2026.3-py2.py3-none-any.whl (348 kB)
Downloading chardet-7.4.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (888 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 888.3/888.3 kB 172.9 MB/s  0:00:00
Downloading et_xmlfile-2.0.0-py3-none-any.whl (18 kB)
Downloading humanize-4.16.0-py3-none-any.whl (137 kB)
Downloading wcwidth-0.8.2-py3-none-any.whl (323 kB)
Installing collected packages: pytz, phonenumbers, passlib, xlsxwriter, wrapt, websockets, wcwidth, vine, uvloop, urllib3, uritemplate, tzdata, typing_extensions, tornado, six, redis, PyYAML, python-multipart, python-http-client, python-dotenv, pyparsing, PyJWT, Pygments, pycparser, pyasn1, psycopg2-binary, protobuf, propcache, prometheus-client, pluggy, pillow, packaging, oauthlib, multidict, maxminddb, MarkupSafe, iniconfig, idna, humanize, httptools, h11, greenlet, frozenlist, et-xmlfile, dnspython, click, charset-normalizer, chardet, certifi, cachetools, billiard, bcrypt, attrs, annotated-types, annotated-doc, aiohappyeyeballs, yarl, Werkzeug, uvicorn, typing-inspection, SQLAlchemy, rsa, requests, reportlab, python-dateutil, pytest, pydantic_core, pyasn1_modules, proto-plus, prompt-toolkit, openpyxl, Mako, httplib2, httpcore, googleapis-common-protos, email-validator, ecdsa, deprecated, click-plugins, click-didyoumean, cffi, anyio, amqp, aiosignal, watchfiles, starlette, requests-oauthlib, python-jose, pytest-asyncio, pydantic, limits, kombu, httpx, google-auth, cryptography, croniter, click-repl, alembic, aiohttp, slowapi, sendgrid, rq, pydantic-settings, google-auth-oauthlib, google-auth-httplib2, google-api-core, geoip2, fastapi, celery, aiohttp-retry, twilio, google-api-python-client, flower

Successfully installed Mako-1.3.10 MarkupSafe-3.0.3 PyJWT-2.10.1 PyYAML-6.0.3 Pygments-2.19.2 SQLAlchemy-2.0.45 Werkzeug-3.1.4 aiohappyeyeballs-2.6.1 aiohttp-3.13.2 aiohttp-retry-2.9.1 aiosignal-1.4.0 alembic-1.17.2 amqp-5.3.1 annotated-doc-0.0.4 annotated-types-0.7.0 anyio-4.12.0 attrs-25.4.0 bcrypt-5.0.0 billiard-4.2.4 cachetools-6.2.2 celery-5.4.0 certifi-2025.11.12 cffi-2.0.0 chardet-7.4.3 charset-normalizer-3.4.4 click-8.3.1 click-didyoumean-0.3.1 click-plugins-1.1.1.2 click-repl-0.3.0 croniter-6.0.0 cryptography-46.0.3 deprecated-1.3.1 dnspython-2.8.0 ecdsa-0.19.1 email-validator-2.3.0 et-xmlfile-2.0.0 fastapi-0.124.2 flower-2.0.1 frozenlist-1.8.0 geoip2-5.2.0 google-api-core-2.28.1 google-api-python-client-2.187.0 google-auth-2.41.1 google-auth-httplib2-0.2.1 google-auth-oauthlib-1.2.3 googleapis-common-protos-1.72.0 greenlet-3.3.0 h11-0.16.0 httpcore-1.0.9 httplib2-0.31.0 httptools-0.7.1 httpx-0.28.1 humanize-4.16.0 idna-3.11 iniconfig-2.3.0 kombu-5.6.2 limits-5.8.0 maxminddb-3.0.0 multidict-6.7.0 oauthlib-3.3.1 openpyxl-3.1.5 packaging-25.0 passlib-1.7.4 phonenumbers-9.0.20 pillow-11.1.0 pluggy-1.6.0 prometheus-client-0.25.0 prompt-toolkit-3.0.52 propcache-0.4.1 proto-plus-1.26.1 protobuf-6.33.2 psycopg2-binary-2.9.11 pyasn1-0.6.1 pyasn1_modules-0.4.2 pycparser-2.23 pydantic-2.12.5 pydantic-settings-2.12.0 pydantic_core-2.41.5 pyparsing-3.2.5 pytest-9.0.2 pytest-asyncio-1.3.0 python-dateutil-2.9.0.post0 python-dotenv-1.2.1 python-http-client-3.3.7 python-jose-3.5.0 python-multipart-0.0.20 pytz-2025.2 redis-7.1.0 reportlab-4.2.5 requests-2.32.5 requests-oauthlib-2.0.0 rq-2.6.1 rsa-4.9.1 sendgrid-6.12.5 six-1.17.0 slowapi-0.1.9 starlette-0.50.0 tornado-6.5.7 twilio-9.8.8 typing-inspection-0.4.2 typing_extensions-4.15.0 tzdata-2026.3 uritemplate-4.2.0 urllib3-2.6.2 uvicorn-0.38.0 uvloop-0.22.1 vine-5.1.0 watchfiles-1.1.1 wcwidth-0.8.2 websockets-15.0.1 wrapt-2.2.2 xlsxwriter-3.2.0 yarl-1.22.0
No broken requirements found.
Checking Python syntax...
Checking for committed private keys...
Applying migrations to the CI database...
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 664debb5246d, Initial database schema
INFO  [alembic.runtime.migration] Running upgrade 664debb5246d -> 43f450d0d72e, Add webhook_logs table
INFO  [alembic.runtime.migration] Running upgrade 43f450d0d72e -> 9242b1ed3f37, Add import_history table
INFO  [alembic.runtime.migration] Running upgrade 9242b1ed3f37 -> 685c3f23b276, Add notification tables
INFO  [alembic.runtime.migration] Running upgrade 685c3f23b276 -> fb2e85ecc260, Add advanced features tables (notes, tags, custom fields, scoring)
INFO  [alembic.runtime.migration] Running upgrade fb2e85ecc260 -> be474161a1a0, phase13_reports_and_exports
INFO  [alembic.runtime.migration] Running upgrade be474161a1a0 -> a31092c4a1b3, add has_whatsapp fields to assets
INFO  [alembic.runtime.migration] Running upgrade a31092c4a1b3 -> 09047e8fa54c, add whatsapp_details_richtext to clients
Running application health smoke test...
/opt/hostedtoolcache/Python/3.12.13/x64/lib/python3.12/site-packages/requests/__init__.py:113: RequestsDependencyWarning: urllib3 (2.6.2) or chardet (7.4.3)/charset_normalizer (3.4.4) doesn't match a supported version!
  warnings.warn(
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
  File "/home/runner/work/leadex/leadex/app/main.py", line 8, in <module>
    from app.api.admin import router as admin_router
  File "/home/runner/work/leadex/leadex/app/api/admin/__init__.py", line 2, in <module>
    from app.api.admin import auth, clients, leads, stats, analytics, webhooks, imports, notifications, advanced, performance, reports
  File "/home/runner/work/leadex/leadex/app/api/admin/imports.py", line 13, in <module>
    from app.services.import_service import ImportService
  File "/home/runner/work/leadex/leadex/app/services/import_service.py", line 5, in <module>
    import pandas as pd
ModuleNotFoundError: No module named 'pandas'
```
