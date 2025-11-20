//✅ 2️⃣ Second Largest Number in Array — C Program

// #include <stdio.h>

// int main() {
//     int n;

//     // Ask user to enter size
//     printf("Enter how many numbers: ");
//     scanf("%d", &n);

//     int arr[n];

//     // Accept list of numbers from user
//     printf("Enter %d numbers:\n", n);
//     for (int i = 0; i < n; i++) {
//         scanf("%d", &arr[i]);
//     }

//     int largest = arr[0];
//     int second = arr[0];

//     // Find second largest
//     for (int i = 1; i < n; i++) {
//         if (arr[i] > largest) {
//             second = largest;
//             largest = arr[i];
//         }
//         else if (arr[i] > second && arr[i] != largest) {
//             second = arr[i];
//         }
//     }

//     printf("Second Largest Number = %d", second);

//     return 0;
// }

#include<stdio.h>

int main()
{
    int n;

    printf("enter the  Array  Count number:");
    
    scanf("%d",&n);

    int Arr[n];

    printf("enter the number:\n",n);
    for(int i=0;i<n;i++)
    {
        scanf("%d",&Arr[i]);
    }

    int Largest = Arr[0];
    int SecondLargest = Arr[0];

    ///  find second largest 

    for(int i=1;i<n;i++)
    {
        if(Arr[i] > Largest)
        {
            SecondLargest = Largest;
            Largest = Arr[i];
        }
        else if(Arr[i] > SecondLargest && Arr[i] != Largest)

        {
            SecondLargest = Arr[i];

        }
    }

    printf("Second Largest number is :%d",SecondLargest);

    return 0;

}