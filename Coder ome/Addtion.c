#include<stdio.h>

int Addition(int iNo1,int iNo2)
{
    int iAns= 0;
    
    iAns = iNo1+iNo2;
    return iAns;
}
int main()

{
    int ivalue1= 0;
    int ivalue2 = 0;
    int iRet = 0;


    printf("enter the first number:\n");
    scanf("%d",&ivalue1);

    printf("Enter the second number :\n");
    scanf("%d",&ivalue2);

    iRet = Addition(ivalue1,ivalue2);

    printf("Addition of this two number is :%d\t",iRet);

    return 0;

}