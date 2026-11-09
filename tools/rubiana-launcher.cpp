// Lancador da Rubiana para Windows: abre a janela sem mostrar a tela preta do console.
// Le a rede em rede.txt (testnet, principal ou regtest) e inicia o programa com o Python do pacote.
#include <windows.h>

#include <string>

static std::wstring PastaDoExe()
{
    wchar_t buf[32768];
    DWORD n = GetModuleFileNameW(nullptr, buf, 32768);
    std::wstring s(buf, n);
    size_t p = s.find_last_of(L"\\/");
    return p == std::wstring::npos ? std::wstring(L".") : s.substr(0, p);
}

static std::wstring LerRede(const std::wstring& pasta)
{
    std::wstring rede = L"testnet";
    HANDLE h = CreateFileW((pasta + L"\\rede.txt").c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (h == INVALID_HANDLE_VALUE) return rede;
    char buf[64] = {0};
    DWORD n = 0;
    ReadFile(h, buf, sizeof(buf) - 1, &n, nullptr);
    CloseHandle(h);
    std::string t;
    for (DWORD i = 0; i < n; ++i) {
        char c = buf[i];
        if (c >= 'a' && c <= 'z') t += c;
        else if (!t.empty()) break;
    }
    if (t == "principal") rede = L"principal";
    else if (t == "regtest") rede = L"regtest";
    return rede;
}

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int)
{
    const std::wstring pasta = PastaDoExe();
    const std::wstring rede = LerRede(pasta);
    std::wstring cmd = L"\"" + pasta + L"\\python\\pythonw.exe\" \"" + pasta + L"\\tools\\rubiana-app.py\" --rede " + rede +
                       L" --config \"" + pasta + L"\\configuracao.txt\"";
    STARTUPINFOW si = {};
    si.cb = sizeof(si);
    PROCESS_INFORMATION pi = {};
    if (!CreateProcessW(nullptr, &cmd[0], nullptr, nullptr, FALSE, CREATE_NO_WINDOW, nullptr, pasta.c_str(), &si, &pi)) {
        MessageBoxW(nullptr, L"Nao consegui iniciar a Rubiana. Confira se a pasta foi extraida por completo (botao direito no .zip, Extrair tudo).", L"Rubiana", MB_OK | MB_ICONERROR);
        return 1;
    }
    if (WaitForSingleObject(pi.hProcess, 10000) == WAIT_OBJECT_0) {
        DWORD code = 0;
        GetExitCodeProcess(pi.hProcess, &code);
        if (code != 0) {
            MessageBoxW(nullptr, L"A Rubiana fechou ao iniciar. Veja o arquivo janela.log na pasta %LOCALAPPDATA%\\Rubiana.", L"Rubiana", MB_OK | MB_ICONERROR);
        }
    }
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return 0;
}
