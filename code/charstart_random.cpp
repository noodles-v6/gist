#include <iostream>
#include <string.h>
#include <stdio.h>
#include <fcntl.h>

using namespace std;

string generate(const char startWithChar)
{
    int charLen = 0;
    bool bStartCharValid = false;
    
    if ('7' != startWithChar && '8' != startWithChar)
    {
        charLen = 9;
    }
    else
    {
        charLen = 9 - 1;
        bStartCharValid = true;
    }
    
    const int BUF_LEN  = 32;
    char rndch[BUF_LEN];    // Passcode 长度是： [9, 16]

    while (1)
    {
        int i = 0;
        int fd = open("/dev/urandom", O_RDONLY);
        if (fd != -1)
        {
            read(fd, rndch, charLen);

            // 将从startWithChars对应的char数据中随机选一个作为首字符
            if (bStartCharValid)
            {
                rndch[i] = startWithChar;
                ++i;
            }

            for (; i < 9; ++i)
            {
                rndch[i] = (char)(((rndch[i] & 0x0f) % 10) + '0');
            }
        }
        else
        {
            close(fd);
            continue;
        }
        close(fd);

        rndch[i] = '\0';
        break;
    }
    return string(rndch);
}

int main()
{
    cout << generate('7') << endl;
    cout << generate('8') << endl;
    cout << generate(0) << endl;
    
    return 0;
}

