@echo off
REM ============================================================
REM HYGMA Experiment Launcher - Phase A+B
REM Each run: 100K timesteps, ~35-45 min CPU
REM ============================================================
set PYTHON=python
set SRC=%~dp0src
set LOGDIR=%~dp0results

echo HYGMA Experiment Matrix
echo ========================
echo Phase A - 3m re-validation (fixed clustering)
echo Phase B - 5m_vs_6m generalization
echo.

set /p CHOICE="Enter: a1 a2 a3 a4 b1 b2 b3 b4 all_a all_b all (or q): "

if "%CHOICE%"=="q" exit /b

cd /d %SRC%

REM ============================================================
REM Phase A: 3m (3 agents)
REM ============================================================
if "%CHOICE%"=="a1" goto :a1
if "%CHOICE%"=="a2" goto :a2
if "%CHOICE%"=="a3" goto :a3
if "%CHOICE%"=="a4" goto :a4
if "%CHOICE%"=="all_a" goto :all_a

REM ============================================================
REM Phase B: 5m_vs_6m (5 agents)
REM ============================================================
if "%CHOICE%"=="b1" goto :b1
if "%CHOICE%"=="b2" goto :b2
if "%CHOICE%"=="b3" goto :b3
if "%CHOICE%"=="b4" goto :b4
if "%CHOICE%"=="all_b" goto :all_b

if "%CHOICE%"=="all" goto :all
echo Invalid choice: %CHOICE%
exit /b

REM === Phase A ===
:a1
echo [A1] 3m dynamic (fixed bug) seed=1
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=3m t_max=100000 test_interval=5000 seed=1 grouping_mode=dynamic
goto :end

:a2
echo [A2] 3m all_one seed=1
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=3m t_max=100000 test_interval=5000 seed=1 grouping_mode=all_one
goto :end

:a3
echo [A3] 3m each_alone seed=1
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=3m t_max=100000 test_interval=5000 seed=1 grouping_mode=each_alone
goto :end

:a4
echo [A4] 3m QMIX baseline seed=1
%PYTHON% main.py --config=qmix --env-config=sc2 with env_args.map_name=3m t_max=100000 test_interval=5000 seed=1
goto :end

REM === Phase B ===
:b1
echo [B1] 5m_vs_6m dynamic (fixed bug) seed=1
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=5m_vs_6m t_max=100000 test_interval=5000 seed=1 grouping_mode=dynamic
goto :end

:b2
echo [B2] 5m_vs_6m all_one seed=1
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=5m_vs_6m t_max=100000 test_interval=5000 seed=1 grouping_mode=all_one
goto :end

:b3
echo [B3] 5m_vs_6m each_alone seed=1
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=5m_vs_6m t_max=100000 test_interval=5000 seed=1 grouping_mode=each_alone
goto :end

:b4
echo [B4] 5m_vs_6m QMIX baseline seed=1
%PYTHON% main.py --config=qmix --env-config=sc2 with env_args.map_name=5m_vs_6m t_max=100000 test_interval=5000 seed=1
goto :end

REM === Batch modes ===
:all_a
echo Running all Phase A experiments sequentially...
echo [A1] 3m dynamic...
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=3m t_max=100000 test_interval=5000 seed=1 grouping_mode=dynamic
echo [A2] 3m all_one...
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=3m t_max=100000 test_interval=5000 seed=1 grouping_mode=all_one
echo [A4] 3m QMIX...
%PYTHON% main.py --config=qmix --env-config=sc2 with env_args.map_name=3m t_max=100000 test_interval=5000 seed=1
goto :end

:all_b
echo Running all Phase B experiments sequentially...
echo [B1] 5m_vs_6m dynamic...
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=5m_vs_6m t_max=100000 test_interval=5000 seed=1 grouping_mode=dynamic
echo [B2] 5m_vs_6m all_one...
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=5m_vs_6m t_max=100000 test_interval=5000 seed=1 grouping_mode=all_one
echo [B3] 5m_vs_6m each_alone...
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=5m_vs_6m t_max=100000 test_interval=5000 seed=1 grouping_mode=each_alone
echo [B4] 5m_vs_6m QMIX...
%PYTHON% main.py --config=qmix --env-config=sc2 with env_args.map_name=5m_vs_6m t_max=100000 test_interval=5000 seed=1
goto :end

:all
echo Running ALL experiments sequentially (A1-A4 + B1-B4)...
echo [A1] 3m dynamic...
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=3m t_max=100000 test_interval=5000 seed=1 grouping_mode=dynamic
echo [A2] 3m all_one...
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=3m t_max=100000 test_interval=5000 seed=1 grouping_mode=all_one
echo [A4] 3m QMIX...
%PYTHON% main.py --config=qmix --env-config=sc2 with env_args.map_name=3m t_max=100000 test_interval=5000 seed=1
echo [B1] 5m_vs_6m dynamic...
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=5m_vs_6m t_max=100000 test_interval=5000 seed=1 grouping_mode=dynamic
echo [B2] 5m_vs_6m all_one...
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=5m_vs_6m t_max=100000 test_interval=5000 seed=1 grouping_mode=all_one
echo [B3] 5m_vs_6m each_alone...
%PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=5m_vs_6m t_max=100000 test_interval=5000 seed=1 grouping_mode=each_alone
echo [B4] 5m_vs_6m QMIX...
%PYTHON% main.py --config=qmix --env-config=sc2 with env_args.map_name=5m_vs_6m t_max=100000 test_interval=5000 seed=1
goto :end

:end
echo.
echo ============================================================
echo Experiment complete: %date% %time%
echo ============================================================
