/// check latter is capital or small 

#include<stdio.h>
void CheckLetter(char ch)
{
    if(ch >= 'A' && ch <= 'Z')
    {
        printf("Letter is Capital:\n");
    }
    else if (ch >= 'a' && ch <= 'z')
    {
        printf("Selected Letter is Small:\n");
    }
    else
    {
     printf("Not a letter.\n");
    }
}

int main()
{
    char ch = 0;

    printf("please first letter....");
    scanf("%c",&ch);

    CheckLetter(ch);   /// function call 

    return 0;

}