#include <iostream>
#include <string.h>
#include <stdio.h>
#include <fcntl.h>

using namespace std;

string genNumericRandom(int charLen)
{
    const int BUF_LEN  = 32;
    char rndch[BUF_LEN];   
    
    while (1)
    {
        int i = 0;
        int fd = open("/dev/urandom", O_RDONLY);
        
        if (fd != -1)
        {
            read(fd, rndch, charLen);

            for (; i < charLen; ++i)
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
    cout << genNumericRandom(6) << endl;
    cout << genNumericRandom(7) << endl;
    cout << genNumericRandom(7) << endl;
    
    return 0;
}

