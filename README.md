## API 목록

http://gypark.gifty4u.com/swagger

API 목록 페이지에서 구현된 API를 테스트할 수 있습니다.

또한 api url로 직접 접속하여 테스트할 수 있습니다(ex http://gypark.gifty4u.com/products). 

## 인증

현재 방식은 header에 직접 토큰을 넣는 방식입니다.

인증이 필요한 API는 "Authorization" 헤더 값으로 "Bearer {access_token}"을 넣어주세요.

브라우저에서 테스트시 [ModHeader][https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj?hl=ko] 크롬 확장 프로그램이 유용합니다.

또한 소셜 로그인이 완전히 개발되기 전 까지 http://gypark.gifty4u.com/login에서 임시로 토큰을 발급할 수 있도록 만들었습니다.

## 관리자 페이지

http://gypark.gifty4u.com/admin