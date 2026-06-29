@echo off
REM HYGMA Experiment Launcher
REM Usage: run_exp.bat <map> <mode> [seed]
REM Example: run_exp.bat 3m dynamic 1

set MAP=%1
set MODE=%2
set SEED=%3
if "%SEED%"=="" set SEED=1

set PYTHON=D:\Soft\Anaconda\envs\hygma\python.exe
set SRC=D:\Project\paper\代码\HYGMA\src
set LOGDIR=D:\Project\paper\代码\HYGMA\results

echo ============================================
echo HYGMA Experiment: map=%MAP% mode=%MODE% seed=%SEED%
echo Start: %date% %time%
echo ============================================

cd /d %SRC%

if "%MODE%"=="qmix" (
    %PYTHON% main.py --config=qmix --env-config=sc2 with env_args.map_name=%MAP% t_max=100000 test_interval=5000 seed=%SEED%
) else (
    %PYTHON% main.py --config=hygma --env-config=sc2 with env_args.map_name=%MAP% t_max=100000 test_interval=5000 seed=%SEED% grouping_mode=%MODE%
)

echo ============================================
echo End: %date% %time%
echo ============================================
