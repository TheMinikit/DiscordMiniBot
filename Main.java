import java.util.InputMismatchException;
import java.util.Scanner;

public class Main {

    public static void main(String args[]) {

        int fromYear = 0;
        int toYear = 0;
        boolean DoubleCheck = false;
        while (!DoubleCheck) {
            fromYear = GetInputInteger("Please input 'from Year':  ");
            toYear = GetInputInteger("Please input 'To Year':  ");
            if (toYear > fromYear) {
                DoubleCheck = true;
            }
        }
        printBonusDatesBetween(fromYear, toYear);

    }

    static void printBonusDatesBetween(int fromYear, int toYear) {

        int ReverseNumber;
        char[] NumberChars;
        int MaxMonths = 12;
        int Number;
        int[] MonthDays = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
        for (int i = fromYear; i <= toYear; i++) {
            for (int i2 = 1; i2 <= MaxMonths; i2++) {
                for (int i3 = 1; i3 <= MonthDays[i2]; i3++) {
                    Number = (i * 10000) + (i2 * 100) + i3;
                    ReverseNumber = ReverseInteger(Number);
                    if (ReverseNumber == Number) {
                        System.out.println(BeatifyDate(Number));
                    }
                }
            }
        }
    }

    public static int GetInputInteger(String InputText) {

        Scanner scanner = new Scanner(System.in);
        boolean CorrectInput = false;
        int InputInteger = 0;
        System.out.print(InputText);
        InputInteger = scanner.nextInt();
        return InputInteger;
    }

    public static int ReverseInteger(int Number) {

        String ReverseString = "";
        char[] CharArray = String.valueOf(Number).toCharArray();
        for (int i = CharArray.length - 1; i >= 0; i--) {
            ReverseString += CharArray[i];
        }
        return Integer.parseInt(ReverseString);

    }

    public static String BeatifyDate(int Number) {

        String BeautifiedDate = "";
        String NumberString = String.valueOf(Number);
        for (int i = 0; i < NumberString.length() - 4; i++) {
            BeautifiedDate += NumberString.charAt(i);
        }
        BeautifiedDate += "-";
        BeautifiedDate += NumberString.charAt(NumberString.length() - 4);
        BeautifiedDate += NumberString.charAt(NumberString.length() - 3);
        BeautifiedDate += "-";
        BeautifiedDate += NumberString.charAt(NumberString.length() - 2);
        BeautifiedDate += NumberString.charAt(NumberString.length() - 1);
        return BeautifiedDate;
    }

}
