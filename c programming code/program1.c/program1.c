// #include<stdio.h>
// void Display(int iNo1)
// {
//     int iCnt = 0;

//     for(iCnt=1;iCnt<=iNo1;iCnt++)
//     {
//         if(iNo1 % 2 == 0)
//         {
//            printf("%d\t",iNo1*iCnt);
//         }
    
//     }
//       printf("\n");
// }

// int main()
       
// {
//     int ivalue1 = 0;

//     printf("enter the first number:\n");
//     scanf("%d",&ivalue1);

//     Display(ivalue1);

//     return 0;

// }

#include <stdio.h>

void Display(int iNo1)
{
    int iCnt = 0;

    for (iCnt = 1; iCnt <= iNo1; iCnt++)
    {
        if (iNo1 % 2 == 0)
        {
            printf("%d\t", iNo1 * iCnt);
        }
    }

    printf("\n");
}

int main()
{
    int ivalue1 = 0;

    printf("Enter a number:\n");
    scanf("%d", &ivalue1);

    Display(ivalue1);

    return 0;
}
