# Proyecto Java Consolidado

**Generado:** 2025-10-28 14:30:00

**Proyecto:** ejemplo-spring-boot

**Ruta:** `C:\Users\Usuario\Proyectos\ejemplo-spring-boot`

**Modo de conversión:** Proyecto completo

## 📋 Metadata del Proyecto

- **Tipo de proyecto:** Maven
- **Total de archivos:** 8

## 📁 Estructura de Directorios

```
📁 pom.xml
📁 src
  📁 main
    📁 java
      📁 com
        📁 example
          📁 demo
            📄 DemoApplication.java
            📄 controller
              📄 HelloController.java
            📄 model
              📄 User.java
            📄 service
              📄 UserService.java
    📁 resources
      📄 application.properties
      📄 application.yml
  📁 test
    📁 java
      📁 com
        📁 example
          📁 demo
            📄 DemoApplicationTests.java
```

## 📄 Contenido de Archivos

---

### 📄 `pom.xml`

**Líneas:** 45 | **Tipo:** .xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>demo</name>
    <description>Demo project for Spring Boot</description>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

---

### 📄 `src/main/java/com/example/demo/DemoApplication.java`

**Líneas:** 12 | **Tipo:** .java

```java
package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

---

### 📄 `src/main/java/com/example/demo/controller/HelloController.java`

**Líneas:** 28 | **Tipo:** .java

```java
package com.example.demo.controller;

import com.example.demo.model.User;
import com.example.demo.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
public class HelloController {

    @Autowired
    private UserService userService;

    @GetMapping("/hello")
    public String hello() {
        return "Hello World!";
    }

    @GetMapping("/users")
    public List<User> getAllUsers() {
        return userService.getAllUsers();
    }

    @GetMapping("/users/{id}")
    public User getUserById(@PathVariable Long id) {
        return userService.getUserById(id);
    }

    @PostMapping("/users")
    public User createUser(@RequestBody User user) {
        return userService.createUser(user);
    }
}
```

---

### 📄 `src/main/java/com/example/demo/model/User.java`

**Líneas:** 42 | **Tipo:** .java

```java
package com.example.demo.model;

import jakarta.persistence.*;

@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    private Integer age;

    // Constructor vacío requerido por JPA
    public User() {
    }

    public User(String name, String email, Integer age) {
        this.name = name;
        this.email = email;
        this.age = age;
    }

    // Getters y Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public Integer getAge() { return age; }
    public void setAge(Integer age) { this.age = age; }
}
```

---

### 📄 `src/main/java/com/example/demo/service/UserService.java`

**Líneas:** 35 | **Tipo:** .java

```java
package com.example.demo.service;

import com.example.demo.model.User;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Service
public class UserService {

    private List<User> users = new ArrayList<>();
    private Long nextId = 1L;

    public List<User> getAllUsers() {
        return new ArrayList<>(users);
    }

    public User getUserById(Long id) {
        return users.stream()
                .filter(user -> user.getId().equals(id))
                .findFirst()
                .orElse(null);
    }

    public User createUser(User user) {
        user.setId(nextId++);
        users.add(user);
        return user;
    }

    public void deleteUser(Long id) {
        users.removeIf(user -> user.getId().equals(id));
    }
}
```

---

### 📄 `src/main/resources/application.properties`

**Líneas:** 5 | **Tipo:** .properties

```properties
spring.application.name=demo
server.port=8080
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
logging.level.org.springframework.web=DEBUG
```

---

### 📄 `src/main/resources/application.yml`

**Líneas:** 10 | **Tipo:** .yml

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
    username: sa
    password: password
  h2:
    console:
      enabled: true
      path: /h2-console
```

---

### 📄 `src/test/java/com/example/demo/DemoApplicationTests.java`

**Líneas:** 13 | **Tipo:** .java

```java
package com.example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class DemoApplicationTests {

    @Test
    void contextLoads() {
        // Test que verifica que el contexto de Spring se carga correctamente
    }
}
```

---

## 📊 Estadísticas del Proyecto

- **Total de archivos procesados:** 8
- **Total de líneas de código:** 190
- **Archivos Java:** 5
- **Otros archivos:** 3
