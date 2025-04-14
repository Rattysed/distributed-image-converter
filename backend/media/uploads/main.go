package main

import (
	"bufio"
	"crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"math/big"
	"os"
	"strconv"
)

var (
	p *big.Int
	q *big.Int
	e *big.Int
	n *big.Int
	d *big.Int
)

func initRSA() error {
	if e == nil {
		e = big.NewInt(0x10001)
	}

	gen := func(x **big.Int) error {
		if *x != nil {
			return nil
		}

		if x == nil {
			return fmt.Errorf("nil pointer")
		}

		var xx *big.Int
		var err error

		for {
			xx, err = rand.Prime(rand.Reader, 2048)
			if err != nil {
				return err
			}

			pq := new(big.Int).Sub(xx, big.NewInt(1))
			if new(big.Int).GCD(nil, nil, pq, e).Cmp(big.NewInt(1)) == 0 {
				break
			}
		}

		*x = xx
		return nil
	}

	if err := gen(&p); err != nil {
		return err
	}

	if err := gen(&q); err != nil {
		return err
	}

	n = new(big.Int).Mul(p, q)
	phi := new(big.Int).Mul(new(big.Int).Sub(p, big.NewInt(1)), new(big.Int).Sub(q, big.NewInt(1)))
	d = new(big.Int).ModInverse(e, phi)
	return nil
}

func resetRSA() {
	q = nil
	e = nil
	n = nil
	d = nil
}

func BytesToInt(s []byte) *big.Int {
	if i, ok := new(big.Int).SetString(fmt.Sprintf("%x", s), 16); ok {
		return i
	}

	return nil
}

func IntToBytes(i *big.Int) []byte {
	msg, _ := hex.DecodeString(fmt.Sprintf("%x", i))
	return msg
}

func Encrypt(plaintext []byte) ([]byte, error) {
	if message := BytesToInt(plaintext); message != nil {
		return IntToBytes(new(big.Int).Exp(message, e, n)), nil
	}

	return nil, errors.New("failed to encrypt")
}

func Decrypt(ciphertext []byte) ([]byte, error) {
	if message := BytesToInt(ciphertext); message != nil {
		return IntToBytes(new(big.Int).Exp(message, d, n)), nil
	}

	return nil, errors.New("failed to decrypt")
}

func encryptFlag() error {
	flag, err := os.ReadFile("flag.txt")
	if err != nil {
		return err
	}

	if err := initRSA(); err != nil {
		return err
	}

	defer resetRSA()

	encryptedFlag, err := Encrypt(flag)
	if err != nil {
		return err
	}

	fmt.Printf("Hello! I have written this RSA algothm myself. Can you help me to check if its secure enough\n")
	fmt.Printf("n = %s\n", n)
	fmt.Printf("e = %s\n", e)
	fmt.Printf("encrypted message = %x\n\n", encryptedFlag)
	return nil
}

func printMenu() {
	fmt.Printf("Menu:\n")
	fmt.Printf("1. Encrypt message\n")
	fmt.Printf("2. Decrypt message\n")
	fmt.Printf("3. Reset RSA\n")
	fmt.Printf("4. Exit\n")
}

func doEncrypt(s *bufio.Scanner) {
	if err := initRSA(); err != nil {
		panic(err)
	}

	fmt.Printf("Input your message (ended with newline): ")
	if !s.Scan() {
		panic(s.Err())
	}

	ciphertext, err := Encrypt(s.Bytes())
	if err != nil {
		panic(err)
	}

	fmt.Printf("Encrypted message: %x\n", ciphertext)
	fmt.Printf("Public:\ne = %s\nn = %s\n", e, n)
}

func doDecrypt(s *bufio.Scanner) {
	if err := initRSA(); err != nil {
		panic(err)
	}

	fmt.Printf("Input your encrypted message (in hex, ended with newline): ")
	if !s.Scan() {
		panic(s.Err())
	}

	ciphertext := make([]byte, len(s.Bytes())/2)

	n, err := hex.Decode(ciphertext, s.Bytes())
	if err != nil {
		panic(err)
	}
	plaintext, err := Decrypt(ciphertext[:n])
	if err != nil {
		panic(err)
	}

	fmt.Printf("Plaintext message: %s\n\n", plaintext)
}

func doReset() {
	resetRSA()
	fmt.Printf("Done!\n\n")
}

func main() {
	s := bufio.NewScanner(os.Stdin)

	if err := encryptFlag(); err != nil {
		panic(err)
	}

	printMenu()

L:
	for s.Scan() {
		menu, err := strconv.Atoi(s.Text())
		if err != nil {
			panic(err)
		}

		switch menu {
		case 1:
			doEncrypt(s)
		case 2:
			doDecrypt(s)
		case 3:
			doReset()
		default:
			break L
		}
		printMenu()

	}

	fmt.Printf("Bye!\n")
}
