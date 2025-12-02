/// create this pattern

// *  @  @  @
// $  *  @  @
// $  $  *  @
// $  $  $  *

#include<stdio.h>

void Display(int iRow,int iCol)
{
 
    int i = 0;
    int j=0;

    for(i=1;i<=iRow;i++)
    {
        for(j=1;j<=iCol;j++)
        {
            if(i == j)
            {
                printf("*\t");  /// *
            }
            else if(i>j)
            {
                printf("$\t"); /// $
            }
            else
            {
                printf("@\t");  /// @
            }
        }
        printf("\n");

    }

}
int main()

{
    int ivalue1 = 0;
    int ivalue2 = 0;

    printf("enter the first row number:\n");
    scanf("%d",&ivalue1);

    printf("Enter the second Columns number:\n");
    scanf("%d",&ivalue2);

    Display(ivalue1,ivalue2);


    return 0;

}