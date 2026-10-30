# Verificação técnica - 30/10/2026

- `host-buffer-test.txt`: saída real do executável C++ compilado no macOS com `clang++ -std=c++11 -Wall -Wextra -Werror firmware/tests/test_ring.cpp -o firmware/evidence/test_ring_plain`.
- Primeira tentativa com `-fsanitize=address,undefined` ficou sem saída e foi interrompida; não se afirma validação por sanitizers. Teste subsequente sem sanitizers terminou com código zero.
- `platformio-build.log`: compilação ESP32 concluída com SUCCESS em 2,69 s; RAM estática 93.380/327.680 bytes (28,5%), flash 785.065/1.310.720 bytes (59,9%). A RAM dinâmica em runtime não foi medida. Manifesto registra hashes dos binários e fontes.
- `platformio-build-attempt1.log`: primeira compilação falhou porque o filtro de fontes não incluía o arquivo `.ino.cpp` gerado; corrigido em `platformio.ini` e recompilado.
- Nenhuma execução física ou Wokwi por este agente. A tentativa de acesso à sessão browser falhou porque ela estava em uso. Isso não é falha de firmware demonstrada.
- Arquivos extraídos dos ebooks em `docs/edge/cap08-local.txt` e `cap09-local.txt` são material de consulta local ignorado pelo Git; não publicar os ebooks exclusivos do aluno.
