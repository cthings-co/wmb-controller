@echo off
setlocal

:: Set directories
set PROTO_DIR=proto\mb_protocol

:: Compile proto files
protoc -I=%PROTO_DIR% --python_out=generated ^
    %PROTO_DIR%\mb_protocol.proto ^
    %PROTO_DIR%\mb_protocol_answers.proto ^
    %PROTO_DIR%\mb_protocol_commands.proto ^
    %PROTO_DIR%\mb_protocol_enums.proto

if %ERRORLEVEL% EQU 0 (
    echo Protocol buffers compiled successfully
) else (
    echo Error compiling protocol buffers
    echo Error level: %ERRORLEVEL%
)

endlocal