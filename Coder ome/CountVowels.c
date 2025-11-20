// // Count Vowels & Consonants — C Program



// #include <stdio.h>
// #include <ctype.h>

// int main() {
//     char str[200];
//     int vowels = 0, consonants = 0;

//     fgets(str, sizeof(str), stdin);

//     for (int i = 0; str[i] != '\0'; i++) {
//         char ch = tolower(str[i]);

//         if (ch >= 'a' && ch <= 'z') {
//             if (ch=='a' || ch=='e' || ch=='i' || ch=='o' || ch=='u')
//                 vowels++; 
//             else
//                 consonants++;
//         }
//     }

//     printf("Vowels: %d\n", vowels);
//     printf("Consonants: %d\n", consonants);

//     return 0;
// }




// #include <stdio.h>

// int main() {
//     char str[200];
//     int vowels = 0, consonants = 0;
//     int i = 0;

//     printf("Enter any string:\n");
//     fgets(str, sizeof(str), stdin);

//     while (str[i] != '\0') {

//         // Check vowels (both upper and lower case)
//         if (str[i]=='a' || str[i]=='e' || str[i]=='i' || str[i]=='o' || str[i]=='u' ||
//             str[i]=='A' || str[i]=='E' || str[i]=='I' || str[i]=='O' || str[i]=='U') {
            
//             vowels++;
//         }
//         // Check consonants (letters except vowels)
//         else if ((str[i] >= 'a' && str[i] <= 'z') ||
//                  (str[i] >= 'A' && str[i] <= 'Z')) {
            
//             consonants++;
//         }

//         i++; // Move to next character
//     }

//     printf("Vowels: %d\n", vowels);
//     printf("Consonants: %d\n", consonants);

//     return 0;
// }

#include<stdio.h>
int main()
{
   char str [200];
   
   int vowels = 0;
   int Consonants = 0;
   int i = 0;

   printf("Enter the any Array String:\n");

   fgets(str,sizeof(str),stdin);

   while (str[i] != '\0')
   {

    if(str [i]=='a' || str[i]=='e' || str[i]=='i' || str[i]=='o' || str[i]=='u' ||
       str[i]=='A'  || str[i]=='E' || str[i]=='I'|| str[i]=='O' || str[i]=='U')
       {
        vowels++;
       }
       /// Check consonants (only)
       else if((str[i] >= 'a' && str[i] <='z')  ||
                (str[i] >= 'A' || str[i]<='Z'))
                {
                Consonants++;
                }
                i++; // Move  to next character

   }
   printf("Vowels:%d\n",vowels);
   printf("consonants: %d\n",Consonants);
   
    return 0;
}